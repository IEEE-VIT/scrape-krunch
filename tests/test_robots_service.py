"""
Unit tests for RobotsService compliance and crawl-delay enforcement.
Zero external runtime dependencies: runs on pure Python standard library.
"""

import io
import time
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

from robots_service import RobotsService


class TestRobotsService(unittest.TestCase):
    def setUp(self):
        self.service = RobotsService(default_user_agent="ScrapeKrunchBot/1.0", cache_ttl=60.0)

    def tearDown(self):
        self.service.clear_cache()

    def test_extract_host_and_scheme(self):
        scheme, host = self.service.extract_host_and_scheme("https://www.bbc.com/news/business-12345")
        self.assertEqual(scheme, "https")
        self.assertEqual(host, "www.bbc.com")

        scheme, host = self.service.extract_host_and_scheme("http://example.org:8080/test")
        self.assertEqual(scheme, "http")
        self.assertEqual(host, "example.org:8080")

    def test_get_robots_url(self):
        robots_url = self.service.get_robots_url("https://techcrunch.com/2026/01/ai-news/")
        self.assertEqual(robots_url, "https://techcrunch.com/robots.txt")

    @patch("urllib.request.urlopen")
    def test_is_allowed_rules(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = (
            b"User-agent: *\n"
            b"Disallow: /admin/\n"
            b"Disallow: /private/\n"
            b"Allow: /public/\n"
        )
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        # Allowed URLs
        self.assertTrue(self.service.is_allowed("https://example.com/public/article-1"))
        self.assertTrue(self.service.is_allowed("https://example.com/news/story"))

        # Disallowed URLs
        self.assertFalse(self.service.is_allowed("https://example.com/admin/settings"))
        self.assertFalse(self.service.is_allowed("https://example.com/private/data"))

    @patch("urllib.request.urlopen")
    def test_crawl_delay_parsing_and_enforcement(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = (
            b"User-agent: *\n"
            b"Crawl-delay: 1\n"
            b"Allow: /\n"
        )
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        delay = self.service.get_crawl_delay("https://delayed-site.com/page")
        self.assertEqual(delay, 1.0)

        # First request should not sleep
        slept_first = self.service.enforce_crawl_delay("https://delayed-site.com/page1")
        self.assertEqual(slept_first, 0.0)

        # Immediate sequential request to same host should sleep for ~1s
        start = time.time()
        slept_second = self.service.enforce_crawl_delay("https://delayed-site.com/page2")
        elapsed = time.time() - start
        self.assertGreater(slept_second, 0.5)
        self.assertGreaterEqual(elapsed, 0.5)

    @patch("urllib.request.urlopen")
    def test_caching_minimizes_network_requests(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b"User-agent: *\nAllow: /\n"
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        # Fetch 5 URLs on the same domain
        for i in range(5):
            self.service.is_allowed(f"https://fast-site.com/item-{i}")

        # urlopen should only be invoked once because of in-memory caching
        self.assertEqual(mock_urlopen.call_count, 1)

    @patch("urllib.request.urlopen")
    def test_404_status_allows_all(self, mock_urlopen):
        # Simulate HTTP 404 error
        err = urllib.error.HTTPError("https://no-robots.org/robots.txt", 404, "Not Found", {}, None)
        mock_urlopen.side_effect = err

        # If robots.txt returns 404, site has no restrictions
        self.assertTrue(self.service.is_allowed("https://no-robots.org/anything"))

    @patch("urllib.request.urlopen")
    def test_403_status_disallows_all(self, mock_urlopen):
        # Simulate HTTP 403 Forbidden
        err = urllib.error.HTTPError("https://forbidden-site.org/robots.txt", 403, "Forbidden", {}, None)
        mock_urlopen.side_effect = err

        # If robots.txt is 403 Forbidden, crawling is blocked
        self.assertFalse(self.service.is_allowed("https://forbidden-site.org/anything"))

    @patch("urllib.request.urlopen")
    def test_network_failure_fails_open_gracefully(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        # Network failures should fail open gracefully rather than crash
        allowed = self.service.is_allowed("https://timeout-site.org/article")
        self.assertTrue(allowed)

    @patch("urllib.request.urlopen")
    def test_can_fetch_and_wait_composite(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = (
            b"User-agent: *\n"
            b"Disallow: /secret/\n"
            b"Allow: /\n"
        )
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        self.assertTrue(self.service.can_fetch_and_wait("https://api-site.com/public-page"))
        self.assertFalse(self.service.can_fetch_and_wait("https://api-site.com/secret/key"))


if __name__ == "__main__":
    unittest.main()
