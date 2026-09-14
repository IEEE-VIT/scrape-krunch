"""Reddit data-fetching service.

Centralizes all outbound Reddit HTTP calls behind RedditService so callers
work with typed data (RedditPost / RedditComment) and an explicit error
state (RedditResult) instead of parsing raw JSON or catching requests
exceptions inline, and errors are never smuggled into the data itself
(the old get_reddit_posts/get_reddit_comments returned fake posts/strings
like "Error fetching Reddit posts: ..." on failure).
"""

import requests
from dataclasses import dataclass, field
from typing import List, Optional

DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0"}


@dataclass
class RedditPost:
    title: str
    link: str
    content: str
    score: int
    subreddit: str


@dataclass
class RedditComment:
    author: str
    score: int
    body: str

    def format(self) -> str:
        return f"[{self.author}] ({self.score} points): {self.body}"


@dataclass
class RedditResult:
    """Envelope separating a successful payload from an error, so callers can
    branch on `result.error` instead of inspecting the data for sentinel strings."""
    data: list = field(default_factory=list)
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None


class RedditService:
    def __init__(self, session: Optional[requests.Session] = None, timeout: int = 10):
        self.session = session or requests.Session()
        self.timeout = timeout

    def fetch_posts(self, query: str, count: int = 7) -> RedditResult:
        url = f"https://www.reddit.com/search.json?q={query}&sort=hot&limit={count}"
        try:
            response = self.session.get(url, headers=DEFAULT_HEADERS, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as e:
            return RedditResult(error=f"Failed to fetch Reddit posts for '{query}': {e}")

        posts: List[RedditPost] = [
            RedditPost(
                title=f"[r/{child['data']['subreddit']}] {child['data']['title']}",
                link=f"https://www.reddit.com{child['data']['permalink']}",
                content=child['data'].get('selftext', ''),
                score=child['data']['score'],
                subreddit=child['data']['subreddit'],
            )
            for child in payload.get('data', {}).get('children', [])
        ]
        return RedditResult(data=posts)

    def fetch_comments(self, post_url: str, max_comments: int = 50) -> RedditResult:
        json_url = post_url.rstrip('/') + '.json'
        try:
            response = self.session.get(json_url, headers=DEFAULT_HEADERS, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as e:
            return RedditResult(error=f"Failed to fetch comments for '{post_url}': {e}")

        comments: List[RedditComment] = []
        if len(payload) > 1 and 'data' in payload[1]:
            for comment in payload[1]['data']['children'][:max_comments]:
                if comment['kind'] == 't1' and 'body' in comment['data']:
                    comments.append(RedditComment(
                        author=comment['data']['author'],
                        score=comment['data']['score'],
                        body=comment['data']['body'],
                    ))
        return RedditResult(data=comments)


def extract_reddit_content(post: RedditPost) -> str:
    return post.content if post.content else "No text content available."
