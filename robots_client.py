"""Shared robots.txt policy and host pacing for direct scraper requests."""

import logging
import threading
import time
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser


logger = logging.getLogger(__name__)
USER_AGENT = "Mozilla/5.0"


def _request(url, **kwargs):
    import requests
    return requests.get(url, **kwargs)


class RobotsAwareClient:
    def __init__(self, get=None, clock=time.monotonic, sleep=time.sleep):
        self._get = get or _request
        self._clock = clock
        self._sleep = sleep
        self._policies = {}
        self._hosts = {}
        self._lock = threading.Lock()
        self._connections = threading.BoundedSemaphore(3)

    def _request(self, url, **kwargs):
        with self._connections:
            return self._get(url, **kwargs)

    def _policy(self, origin, headers, timeout, state):
        # Called under the host lock: concurrent articles fetch robots only once.
        if origin not in self._policies:
            self._wait(state, state["delay"])
            parser = RobotFileParser(origin + "/robots.txt")
            try:
                response = self._request(
                    parser.url, headers=headers, timeout=timeout,
                    allow_redirects=True,
                )
                try:
                    if response.status_code in (404, 410):
                        parser.parse([])
                    elif 200 <= response.status_code < 300:
                        parser.parse(response.text.splitlines())
                    else:
                        parser = None
                finally:
                    response.close()
            except Exception as exc:
                logger.info("Unable to fetch robots.txt for %s: %s", origin, exc)
                parser = None
            finally:
                state["last"] = self._clock()
            # Unavailable or forbidden robots rules cause a skip for this run.
            self._policies[origin] = parser
        return self._policies[origin]

    def _wait(self, state, delay):
        if state["last"] is not None:
            remaining = max(delay, state["delay"]) - (self._clock() - state["last"])
            if remaining > 0:
                self._sleep(remaining)

    def get(self, url, headers=None, timeout=10):
        """Return a response, or None if robots policy prevents the request."""
        headers = dict(headers or {})
        agent = next((value for key, value in headers.items()
                      if key.lower() == "user-agent"), USER_AGENT)
        headers = {key: value for key, value in headers.items()
                   if key.lower() != "user-agent"}
        headers["User-Agent"] = agent

        for _ in range(11):
            parts = urlsplit(url)
            if parts.scheme not in ("http", "https") or not parts.hostname:
                logger.info("Skipping %s: invalid HTTP URL", url)
                return None
            origin = f"{parts.scheme}://{parts.netloc.lower()}"
            with self._lock:
                state = self._hosts.setdefault(parts.hostname.lower(), {
                    "lock": threading.Lock(), "last": None, "delay": 0,
                })
            with state["lock"]:
                parser = self._policy(origin, headers, timeout, state)
                if parser is None or not parser.can_fetch(agent, url):
                    reason = "robots.txt unavailable" if parser is None else "disallowed by robots.txt"
                    logger.info("Skipping %s: %s (User-Agent: %s)", url, reason, agent)
                    return None
                delay = parser.crawl_delay(agent) or 0
                self._wait(state, delay)
                try:
                    response = self._request(
                        url, headers=headers, timeout=timeout, allow_redirects=False,
                    )
                finally:
                    state["last"] = self._clock()
                    state["delay"] = delay
            if response.status_code in (301, 302, 303, 307, 308) and response.headers.get("Location"):
                url = urljoin(url, response.headers["Location"])
                response.close()
                continue
            response.raise_for_status()
            return response
        logger.info("Skipping %s: too many redirects", url)
        return None


scrape_get = RobotsAwareClient().get
