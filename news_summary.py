import requests
from bs4 import BeautifulSoup as bs
def get_rss_articles(query, count=3):
    rss_url = f"https://news.google.com/rss/search?q={query}"
    response = requests.get(rss_url)
    soup = bs(response.content, "xml")

    items = soup.find_all("item")[:count]
    articles = []

    for item in items:
        title = item.title.text
        link = item.link.text

        try:
            article_response = requests.get(link, timeout=5)
            article_soup = bs(article_response.content, "html.parser")

            # Try to extract the content — naive approach
            paragraphs = article_soup.find_all("p")
            text = " ".join(p.text for p in paragraphs)
        except Exception as e:
            text = f"Failed to fetch content: {e}"

        articles.append({"title": title, "link": link, "content": text})

    return articles

query = input("Enter a keyword: ")
news = get_rss_articles(query)
print(news)