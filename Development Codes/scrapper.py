import requests
from bs4 import BeautifulSoup

class NewsScraper:
    def __init__(self, base_url="https://www.businesstoday.in", user_agent="Mozilla/5.0"):
        self.base_url = base_url
        self.headers = {"User-Agent": user_agent}

    def get_article_links(self, count=5):
        url = f"{self.base_url}/latest"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        anchors = soup.find_all("a", href=True, title=True)
        articles = []

        for tag in anchors:
            href = tag["href"]
            title = tag["title"].strip()
            if "/story/" in href:
                full_url = href if href.startswith("http") else self.base_url + href
                articles.append({"title": title, "link": full_url})
                if len(articles) >= count:
                    break
        return articles

    def extract_article_content(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            article_div = soup.find("div", class_="text-formatted field--name-body")
            if not article_div:
                article_divs = soup.find_all("div", class_=lambda x: x and "field--name-body" in x)
                article_div = article_divs[0] if article_divs else None

            if article_div:
                paragraphs = article_div.find_all("p")
                content = "\n".join(p.get_text(strip=True) for p in paragraphs)
                return content.strip() if content else "❌ Empty article body."
            else:
                return "❌ Article content div not found."
        except Exception as e:
            return f"❌ Error fetching content: {e}"
