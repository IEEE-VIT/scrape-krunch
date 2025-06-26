import requests
from bs4 import BeautifulSoup
from ollama import chat, ChatResponse
import time


BASE_URL = "https://www.businesstoday.in"


def get_article_links(count=5):
    url = f"{BASE_URL}/latest"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    anchors = soup.find_all("a", href=True, title=True)
    articles = []

    for tag in anchors:
        href = tag["href"]
        title = tag["title"].strip()
        if "/story/" in href:
            full_url = href if href.startswith("http") else BASE_URL + href
            articles.append({"title": title, "link": full_url})
            if len(articles) >= count:
                break
    return articles


def extract_article_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Properly identify the article body
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


def analyze_with_llm(title, content):
    if content.startswith("❌") or len(content.split()) < 30:
        return "⚠️ Skipping due to low content."
    try:
        response: ChatResponse = chat(model='llama3.2', messages=[
            {
                'role': 'system',
                'content': """You are a global news analyst.
Given a news article, respond with the following format:
1. Summary: ...
2. Sentiment: Positive / Negative / Neutral
3. Socio-economic Impact: ...
4. Political Impact: ...
5. Stock Market Impact: ...
""",
            },
            {
                'role': 'user',
                'content': f"Title: {title}\n\nContent:\n{content}",
            },
        ])
        return response.message.content
    except Exception as e:
        return f"❌ LLM Error: {e}"


def main():
    print("🔍 Scraping latest Business Today articles...")
    articles = get_article_links(count=5)

    for i, article in enumerate(articles, 1):
        print(f"\n🔹 [{i}] {article['title']}")
        print(f"🔗 {article['link']}")

        content = extract_article_content(article["link"])
        print(f"\n📝 Content Preview:\n{content[:500]}...\n")

        analysis = analyze_with_llm(article["title"], content)
        print(f"🤖 LLM Analysis:\n{analysis}\n")

        print("-----------------------------------------------------\n")
        time.sleep(1)


if __name__ == "__main__":
    main()
