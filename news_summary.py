import requests
from bs4 import BeautifulSoup as bs


def get_rss_articles(query, count):
    rss_url = f"https://news.google.com/rss/search?q={query}"
    response = requests.get(rss_url)
    soup = bs(response.content, "xml")

    items = soup.find_all("item")[:count]
    articles = []

    for item in items:
        title = item.title.text
        link = item.link.text

        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            redirect_response = requests.get(link, headers=headers, timeout=5, allow_redirects=True)
            real_url = redirect_response.url

            article_response = requests.get(real_url, headers=headers, timeout=5)
            article_soup = bs(article_response.content, "html.parser")

            article_tag = article_soup.find("article")
            if article_tag:
                text = article_tag.get_text(separator=" ", strip=True)
            else:
                paragraphs = article_soup.find_all("p")
                text = " ".join(p.text for p in paragraphs[:5]) or "No content found"
        except Exception as e:
            text = f"Failed to fetch content: {e}"

        articles.append({
            "title": title,
            "link": real_url,
            "content": text
        })

    return articles


query = input("Enter a keyword: ")
count = int(input("Enter number of articles you want: "))
news = get_rss_articles(query, count)
print(news)
