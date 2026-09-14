import json
import hashlib
import os
from typing import Dict, Set, Any, Optional
import requests

class ArticleCache:
    MAX_CACHE_SIZE = 50

    def __init__(self, cache_file: str = "article_cache.json", max_size: int = 50):
        self.cache_file = cache_file
        self.MAX_CACHE_SIZE = max_size
        self.cache: Dict[str, Any] = self._load_cache()
        self._check_and_trim_initial_load()

    def _load_cache(self) -> Dict[str, Any]:
        default_cache = {"urls": set(), "title_hashes": set(), "order": []}
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    urls = set(cache_data.get("urls", []))
                    title_hashes = set(cache_data.get("title_hashes", []))
                    order = [list(item) for item in cache_data.get("order", [])]
                    return {"urls": urls, "title_hashes": title_hashes, "order": order}
            except (json.JSONDecodeError, IOError, PermissionError) as e:
                print(f"Warning: Failed to load cache file '{self.cache_file}' ({e}). Starting new cache.")
                return default_cache
        return default_cache

    def _save_cache(self):
        try:
            cache_data = {
                "urls": list(self.cache["urls"]),
                "title_hashes": list(self.cache["title_hashes"]),
                "order": self.cache["order"]
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=4)
        except (IOError, PermissionError) as e:
            print(f"Error: Could not save cache to disk: {e}")

    def _hash_title(self, title: str) -> str:
        return hashlib.md5(title.lower().encode()).hexdigest()

    def _evict_oldest(self):
        if self.cache["order"]:
            oldest_url, oldest_hash = self.cache["order"].pop(0)
            self.cache["urls"].discard(oldest_url)
            self.cache["title_hashes"].discard(oldest_hash)
            print(f"Cache limit ({self.MAX_CACHE_SIZE}) exceeded. Evicted: {oldest_url}")

    def is_article_processed(self, url: str, title: str) -> bool:
        title_hash = self._hash_title(title)
        return url in self.cache["urls"] or title_hash in self.cache["title_hashes"]

    def add_article(self, url: str, title: str):
        if self.is_article_processed(url, title):
            return 
        title_hash = self._hash_title(title)
        self.cache["urls"].add(url)
        self.cache["title_hashes"].add(title_hash)
        self.cache["order"].append([url, title_hash])
        
        if len(self.cache["order"]) > self.MAX_CACHE_SIZE:
            self._evict_oldest()
        self._save_cache()

    def clear_cache(self):
        self.cache = {"urls": set(), "title_hashes": set(), "order": []}
        self._save_cache()
        print("Cache cleared.")

    def _check_and_trim_initial_load(self):
        while len(self.cache["order"]) > self.MAX_CACHE_SIZE:
            self._evict_oldest()
        print(f"Loaded cache with {len(self.cache['order'])} articles.")


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(self, model: str, prompt: str, stream: bool = False) -> Optional[str]:
        endpoint = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }

        try:
            response = requests.post(
                endpoint, 
                json=payload, 
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json().get("response", "")

        except requests.exceptions.Timeout:
            print(
                f"\n[Error] The request to Ollama timed out after {self.timeout} seconds.\n"
                "Please verify that your local Ollama daemon is running, healthy, and not hung on heavy context processing.\n"
                "Run `ollama list` or `systemctl status ollama` to check instance health."
            )
            return None

        except requests.exceptions.ConnectionError:
            print(
                f"\n[Error] Could not connect to Ollama at {self.base_url}.\n"
                "Ensure the Ollama service is started (`ollama serve`)."
            )
            return None

        except requests.exceptions.RequestException as e:
            print(f"\n[Error] HTTP Request to Ollama failed: {e}")
            return None


if __name__ == "__main__":
    # Initialize cache and client
    cache = ArticleCache()
    ollama = OllamaClient(timeout=60)

    article_url = "https://example.com/ai-news"
    article_title = "Local LLMs in 2026"

    if not cache.is_article_processed(article_url, article_title):
        print("Processing article with Ollama...")
        prompt = f"Summarize this article title: {article_title}"
        
        summary = ollama.generate(model="llama3", prompt=prompt)
        
        if summary:
            print(f"Summary: {summary}")
            cache.add_article(article_url, article_title)
    else:
        print("Article already processed. Skipping Ollama dispatch.")