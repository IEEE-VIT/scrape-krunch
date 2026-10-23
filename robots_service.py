"""
Robots.txt compliance and automatic crawl-delay enforcement service.
Integrates urllib.robotparser.RobotFileParser with in-memory caching and per-host rate limiting.
Built purely with standard library components for zero-dependency reliability.
"""

import logging
import time
import urllib.error
import urllib.request
from threading import Lock
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

logger = logging.getLogger("RobotsService")


class RobotsService:
    """
    Manages robots.txt fetching, parsing, caching, and crawl-delay enforcement.
    Uses standard library urllib.robotparser for zero external dependency overhead.
    """

    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    DEFAULT_CACHE_TTL = 3600.0  # Cache robots.txt for 1 hour

    def __init__(
        self,
        default_user_agent: str = DEFAULT_USER_AGENT,
        cache_ttl: float = DEFAULT_CACHE_TTL,
        request_timeout: float = 5.0,
    ):
        self.default_user_agent = default_user_agent
        self.cache_ttl = cache_ttl
        self.request_timeout = request_timeout

        # host -> (RobotFileParser, fetch_timestamp)
        self._cache: Dict[str, Tuple[RobotFileParser, float]] = {}
        # host -> last_request_timestamp (for crawl-delay)
        self._last_request_time: Dict[str, float] = {}
        self._lock = Lock()

    @staticmethod
    def extract_host_and_scheme(url: str) -> Tuple[str, str]:
        """Extract scheme and netloc/host from URL."""
        parsed = urlparse(url)
        scheme = parsed.scheme if parsed.scheme else "https"
        host = parsed.netloc.lower()
        return scheme, host

    def get_robots_url(self, url: str) -> str:
        """Construct the robots.txt URL for a given target URL."""
        scheme, host = self.extract_host_and_scheme(url)
        return f"{scheme}://{host}/robots.txt"

    def get_parser(self, url: str) -> Optional[RobotFileParser]:
        """
        Fetch or retrieve cached RobotFileParser for the given URL's host.
        """
        scheme, host = self.extract_host_and_scheme(url)
        if not host:
            return None

        now = time.time()
        with self._lock:
            if host in self._cache:
                parser, cached_at = self._cache[host]
                if now - cached_at < self.cache_ttl:
                    return parser

        robots_url = f"{scheme}://{host}/robots.txt"
        parser = RobotFileParser()
        parser.set_url(robots_url)

        try:
            req = urllib.request.Request(
                robots_url,
                headers={"User-Agent": self.default_user_agent},
            )
            with urllib.request.urlopen(req, timeout=self.request_timeout) as resp:
                status = resp.status if hasattr(resp, "status") else resp.getcode()
                raw_bytes = resp.read()
                text = raw_bytes.decode("utf-8", errors="replace")
                parser.parse(text.splitlines())
                logger.info(f"Loaded and parsed robots.txt from {robots_url} (HTTP {status})")
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                # Forbidden / Unauthorized: treat entire site as disallowed
                parser.parse(["User-agent: *", "Disallow: /"])
                logger.warning(f"Access to {robots_url} returned HTTP {e.code}; treating host as disallowed.")
            else:
                # 404 Not Found or other 4xx: site has no robots.txt, all crawling is permitted
                parser.parse(["User-agent: *", "Allow: /"])
                logger.info(f"No robots.txt found at {robots_url} (HTTP {e.code}); allowing all paths.")
        except Exception as e:
            # Network or connection error: fail open gracefully with empty parser (allows all)
            logger.warning(f"Failed to fetch robots.txt from {robots_url} ({e}); allowing requests gracefully.")
            parser.parse(["User-agent: *", "Allow: /"])

        with self._lock:
            self._cache[host] = (parser, now)

        return parser

    def is_allowed(self, url: str, user_agent: Optional[str] = None) -> bool:
        """
        Check whether the target URL path is permitted to be scraped under robots.txt.
        """
        ua = user_agent or self.default_user_agent
        parser = self.get_parser(url)
        if not parser:
            return True

        allowed = parser.can_fetch(ua, url)
        if not allowed:
            logger.info(f"[Robots.txt] Disallowed: Scraping {url} is prohibited for user-agent '{ua}'. Skipping.")
        return allowed

    def get_crawl_delay(self, url: str, user_agent: Optional[str] = None) -> Optional[float]:
        """
        Extract crawl-delay directive for the domain, if configured.
        """
        ua = user_agent or self.default_user_agent
        parser = self.get_parser(url)
        if not parser:
            return None

        try:
            delay = parser.crawl_delay(ua)
            if delay is not None:
                return float(delay)
        except Exception:
            pass

        return None

    def enforce_crawl_delay(self, url: str, user_agent: Optional[str] = None) -> float:
        """
        Sleeps if necessary to respect the Crawl-delay directive for the domain.
        Returns the duration slept in seconds (0.0 if no sleep was needed).
        """
        scheme, host = self.extract_host_and_scheme(url)
        if not host:
            return 0.0

        delay = self.get_crawl_delay(url, user_agent)
        if not delay or delay <= 0:
            return 0.0

        slept = 0.0
        with self._lock:
            now = time.time()
            last_time = self._last_request_time.get(host, 0.0)
            elapsed = now - last_time
            if elapsed < delay:
                sleep_needed = delay - elapsed
                logger.info(f"[Robots.txt] Enforcing {delay}s crawl-delay for {host}. Sleeping {sleep_needed:.2f}s...")
                time.sleep(sleep_needed)
                slept = sleep_needed

            self._last_request_time[host] = time.time()

        return slept

    def can_fetch_and_wait(self, url: str, user_agent: Optional[str] = None) -> bool:
        """
        Convenience method: checks if URL is allowed, and if allowed, enforces any crawl-delay.
        Returns True if permitted to proceed, or False if disallowed.
        """
        if not self.is_allowed(url, user_agent):
            return False

        self.enforce_crawl_delay(url, user_agent)
        return True

    def clear_cache(self):
        """Clear cached parsers and rate limiting timers."""
        with self._lock:
            self._cache.clear()
            self._last_request_time.clear()
