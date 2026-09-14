import ast
from pathlib import Path
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock

from robots_client import RobotsAwareClient
import robots_client


def response(text="", status=200, location=None):
    return Mock(text=text, status_code=status,
                headers={"Location": location} if location else {})


class RobotsTests(unittest.TestCase):
    def test_all_scrapers_handle_skipped_requests(self):
        path = Path(robots_client.__file__).with_name("main.py")
        tree = ast.parse(path.read_text(encoding="utf-8"))
        checked = 0
        for function in tree.body:
            if not isinstance(function, ast.FunctionDef):
                continue
            calls = [node for node in ast.walk(function)
                     if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                     and node.func.id == "scrape_get"]
            if not calls:
                continue
            with self.subTest(function=function.name):
                parser = Mock()
                namespace = {"scrape_get": Mock(return_value=None), "BeautifulSoup": parser}
                exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), "exec"), namespace)
                args = ("https://site.test/a",) if function.name.startswith("extract_") or function.name in ("get_reddit_posts", "get_reddit_comments") else ()
                result = namespace[function.name](*args)
                self.assertIn(result, (None, "", [], "No comments available"))
                parser.assert_not_called()
                checked += 1
        self.assertEqual(checked, 13)

    def test_agent_path_and_cache(self):
        get = Mock(side_effect=[response("User-agent: TestBot\nDisallow: /private\n\nUser-agent: *\nDisallow: /"), response()])
        client = RobotsAwareClient(get=get)
        with self.assertLogs("robots_client", level="INFO"):
            self.assertIsNone(client.get("https://site.test/private/a", {"User-Agent": "TestBot/1.0"}))
        self.assertIsNotNone(client.get("https://site.test/public", {"User-Agent": "TestBot/1.0"}))
        self.assertEqual(get.call_count, 2)
        self.assertEqual(get.call_args.kwargs["headers"]["User-Agent"], "TestBot/1.0")

    def test_delay_is_host_local_and_applies_after_robots(self):
        now = [0]
        sleeps = []
        def sleep(delay):
            sleeps.append(delay)
            now[0] += delay
        get = Mock(side_effect=[response("User-agent: *\nCrawl-delay: 3"), response(), response(), response("User-agent: *\nCrawl-delay: 3"), response()])
        client = RobotsAwareClient(get=get, clock=lambda: now[0], sleep=sleep)
        client.get("https://one.test/a")
        client.get("https://one.test/b")
        client.get("https://two.test/a")
        self.assertEqual(sleeps, [3, 3, 3])

    def test_unavailable_rules_skip_and_missing_rules_allow(self):
        for status in (401, 403, 429, 500):
            with self.subTest(status=status):
                get = Mock(return_value=response(status=status))
                client = RobotsAwareClient(get=get)
                self.assertIsNone(client.get("https://site.test/a"))
                self.assertEqual(get.call_count, 1)
        for status in (404, 410):
            get = Mock(side_effect=[response(status=status), response()])
            self.assertIsNotNone(RobotsAwareClient(get=get).get("https://site.test/a"))
        get = Mock(side_effect=TimeoutError("timeout"))
        self.assertIsNone(RobotsAwareClient(get=get).get("https://site.test/a"))

    def test_redirect_target_is_checked_before_fetch(self):
        get = Mock(side_effect=[response(), response(status=302, location="https://other.test/private"), response("User-agent: *\nDisallow: /")])
        self.assertIsNone(RobotsAwareClient(get=get).get("https://site.test/a"))
        self.assertEqual([call.args[0] for call in get.call_args_list], ["https://site.test/robots.txt", "https://site.test/a", "https://other.test/robots.txt"])
        self.assertFalse(get.call_args_list[1].kwargs["allow_redirects"])

    def test_concurrent_requests_share_policy_and_delay(self):
        now = [0]
        starts = []
        robots = []
        def get(url, **kwargs):
            if url.endswith("/robots.txt"):
                robots.append(url)
                return response("User-agent: *\nCrawl-delay: 2")
            starts.append(now[0])
            return response()
        def sleep(delay):
            now[0] += delay
        client = RobotsAwareClient(get=get, clock=lambda: now[0], sleep=sleep)
        with ThreadPoolExecutor(max_workers=3) as pool:
            results = list(pool.map(client.get, [f"https://site.test/{i}" for i in range(6)]))
        self.assertTrue(all(result is not None for result in results))
        self.assertEqual(len(robots), 1)
        self.assertEqual(starts, [2, 4, 6, 8, 10, 12])

    def test_hosts_can_fetch_in_parallel(self):
        barrier = threading.Barrier(3, timeout=3)
        def get(url, **kwargs):
            if not url.endswith("/robots.txt"):
                barrier.wait()
            return response()
        client = RobotsAwareClient(get=get)
        with ThreadPoolExecutor(max_workers=3) as pool:
            self.assertEqual(len(list(pool.map(client.get, [f"https://host{i}.test/a" for i in range(3)]))), 3)


if __name__ == "__main__":
    unittest.main()
