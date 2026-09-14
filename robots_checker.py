"""
robots_checker.py

Provides RobotsComplianceChecker: fetches and caches robots.txt per host,
checks whether a given URL is allowed for our User-Agent, and enforces any
Crawl-delay directive between sequential requests to the same host.

Resolves issue #16 (Dynamic robots.txt compliance and automatic
crawl-delay enforcement).
"""

import time
import urllib.robotparser
from urllib.parse import urlparse
from typing import Dict, Optional


class RobotsComplianceChecker:
    """
    Checks robots.txt permissions for target domains and enforces
    any Crawl-delay directive between sequential requests to the same host.

    Usage:
        checker = RobotsComplianceChecker(user_agent="scrape-krunch-bot")
        if checker.check_and_wait(url):
            response = requests.get(url, ...)
        else:
            # skip - disallowed by robots.txt
            ...
    """

    def __init__(self, user_agent: str = "scrape-krunch-bot", default_delay: float = 0.0):
        self.user_agent = user_agent
        self.default_delay = default_delay  # fallback delay (seconds) when no Crawl-delay is specified
        self._parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}
        self._crawl_delays: Dict[str, Optional[float]] = {}
        self._last_request_time: Dict[str, float] = {}

    @staticmethod
    def _get_host(url: str) -> str:
        return urlparse(url).netloc

    @staticmethod
    def _get_robots_url(url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    def _load_parser(self, url: str) -> urllib.robotparser.RobotFileParser:
        """Fetch + cache the robots.txt parser and crawl-delay for a host."""
        host = self._get_host(url)
        if host not in self._parsers:
            robots_url = self._get_robots_url(url)
            parser = urllib.robotparser.RobotFileParser()
            parser.set_url(robots_url)
            try:
                parser.read()
            except Exception as e:
                # If robots.txt can't be fetched (network error, timeout, etc.),
                # fail open (assume allowed) but log it so it's visible.
                print(f"[robots.txt] Could not fetch/parse {robots_url}: {e}. Assuming allowed.")

            self._parsers[host] = parser

            try:
                delay = parser.crawl_delay(self.user_agent)
            except Exception:
                delay = None

            self._crawl_delays[host] = delay if delay is not None else (self.default_delay or None)

        return self._parsers[host]

    def is_allowed(self, url: str) -> bool:
        """Return True if `url` may be fetched by our User-Agent per robots.txt."""
        try:
            parser = self._load_parser(url)
            return parser.can_fetch(self.user_agent, url)
        except Exception as e:
            print(f"[robots.txt] Error checking permission for {url}: {e}. Assuming allowed.")
            return True

    def get_crawl_delay(self, url: str) -> Optional[float]:
        host = self._get_host(url)
        if host not in self._crawl_delays:
            self._load_parser(url)
        return self._crawl_delays.get(host)

    def wait_for_crawl_delay(self, url: str) -> None:
        """Sleep as needed so consecutive requests to this host respect Crawl-delay."""
        host = self._get_host(url)
        delay = self.get_crawl_delay(url)
        if not delay:
            return

        last_time = self._last_request_time.get(host)
        if last_time is not None:
            elapsed = time.time() - last_time
            remaining = delay - elapsed
            if remaining > 0:
                print(f"[robots.txt] Enforcing crawl-delay of {delay}s for {host} "
                      f"(waiting {remaining:.1f}s)...")
                time.sleep(remaining)

    def mark_request(self, url: str) -> None:
        """Record that a request to this host's just been made (for crawl-delay tracking)."""
        self._last_request_time[self._get_host(url)] = time.time()

    def check_and_wait(self, url: str) -> bool:
        """
        Convenience all-in-one call for use right before requests.get(url, ...):

          - Returns False (and logs an informational message) if `url` is
            disallowed by robots.txt - caller should skip it gracefully.
          - Returns True if allowed, after sleeping for any required
            Crawl-delay and recording the request time.
        """
        if not self.is_allowed(url):
            print(f"[robots.txt] Skipping (disallowed by robots.txt): {url}")
            return False

        self.wait_for_crawl_delay(url)
        self.mark_request(url)
        return True