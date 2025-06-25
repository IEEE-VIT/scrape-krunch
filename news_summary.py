import requests
from bs4 import BeautifulSoup as bs
from newspaper import Article


def extract_clean_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        return f"Failed to extract clean article: {e}"


def get_rss_articles(query, count):
    rss_url = f"https://news.google.com/rss/search?q={query}"
    response = requests.get(rss_url)
    soup = bs(response.content, "xml")

    items = soup.find_all("item")[:count]
    articles = []

    for item in items:
        title = item.title.text
        link = item.link.text.strip()

        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            redirect_response = requests.get(link, headers=headers, timeout=5, allow_redirects=True)
            real_url = redirect_response.url

            # ✅ Extract clean article content using newspaper3k
            text = extract_clean_article(real_url)

        except Exception as e:
            text = f"Failed to fetch content: {e}"
            real_url = link  # fallback to original link if redirect fails

        articles.append({
            "title": title,
            "link": real_url,
            "content": text
        })

    return articles



query = "finance"
article_data = get_rss_articles(query, count=3)

# 🟩 Print the articles
for article in article_data:
    print(f"\n📰 {article['title']}")
    print(f"🔗 {article['link']}")
    print(f"📄 {article['content'][:600]}...\n")