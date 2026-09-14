import argparse
import requests
from bs4 import BeautifulSoup
from ollama import chat, ChatResponse
import time
from duckduckgo_search import DDGS as ddgs
from article_cache import ArticleCache
from reddit_service import RedditService, extract_reddit_content

article_cache = ArticleCache()
reddit_service = RedditService()

FALLBACK_CONTAINER_SELECTORS = [
    ("article", {}),
    ("div", {"class": "article-content"}),
    ("div", {"class": "article-body"}),
    ("div", {"class": "story-body"}),
    ("div", {"class": "entry-content"}),
    ("div", {"class": "post-content"}),
    ("div", {"class": "content-body"}),
    ("div", {"class": "content"}),
    ("main", {}),
]

MIN_MEANINGFUL_CONTENT_LENGTH = 200


def _text_from_container(container, paragraph_limit=None):
    paragraphs = container.find_all("p")
    if paragraph_limit:
        paragraphs = paragraphs[:paragraph_limit]
    return "\n".join(p.get_text(strip=True) for p in paragraphs).strip()


def extract_with_fallback(soup, site_selectors=None, url=""):
    candidates = list(site_selectors or []) + FALLBACK_CONTAINER_SELECTORS

    for tag, attrs in candidates:
        container = soup.find(tag, attrs) if attrs else soup.find(tag)
        if not container:
            continue
        content = _text_from_container(container)
        if len(content) >= MIN_MEANINGFUL_CONTENT_LENGTH:
            return content

    print(f"Warning: no known article container matched for '{url}'. "
          f"Falling back to generic <p> tag extraction.")
    content = _text_from_container(soup, paragraph_limit=10)
    return content if content else "Could not extract content."


def search_duckduckgo(query, max_results=10):
    with ddgs() as ddgs_instance:
        reddit_results = list(ddgs_instance.text(keywords=query, max_results=max_results))
    return reddit_results


def get_article_links(count=3):
    try:
        query = "latest business news 2025"
        print(f"biz articles getting..")

        results = search_duckduckgo(query, max_results=count * 3)
        articles = []

        for result in results:
            if result.get('title') and result.get('href'):
                url = result['href']
                if article_cache.is_article_processed(url, result['title']):
                    print(f"Skipping previously processed article: {result['title']}")
                    continue
                    
                if any(source in url.lower() for source in
                       ['reuters', 'bloomberg', 'wsj', 'marketwatch', 'cnbc', 'yahoo', 'finance']):
                    articles.append({
                        "title": result['title'],
                        "link": url
                    })
                    article_cache.add_article(url, result['title'])
                    if len(articles) >= count:
                        break

        if not articles:
            for result in results:
                if result.get('title') and result.get('href'):
                    if article_cache.is_article_processed(result['href'], result['title']):
                        print(f"Skipping previously processed article: {result['title']}")
                        continue
                    articles.append({
                        "title": result['title'],
                        "link": result['href']
                    })
                    article_cache.add_article(result['href'], result['title'])
                    if len(articles) >= count:
                        break

        return articles if articles else get_fallback_business_news(count)

    except Exception as e:
        print(f" search failed: {e}. fallback...")
        return get_fallback_business_news(count)


def get_fallback_business_news(count=3):
    return [{
        "title": "Business News: Global Markets Show Mixed Performance Amid Economic Uncertainty",
        "link": "https://example.com/business-news"
    }]


def get_bbc_business_articles(count=3):
    url = "https://www.bbc.com/business"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        articles = []
        article_links = soup.find_all("a", href=True)

        for link in article_links:
            href = link.get("href", "")
            if "/news/business-" in href or "/news/articles/" in href:
                title_elem = link.find("h3") or link.find("span") or link
                title = title_elem.get_text(strip=True)

                if title and len(title) > 10:
                    full_url = href if href.startswith("http") else f"https://www.bbc.com{href}"
                    
                    if article_cache.is_article_processed(full_url, title):
                        print(f"Skipping previously processed article: {title}")
                        continue
                        
                    articles.append({"title": title, "link": full_url})
                    article_cache.add_article(full_url, title)

                    if len(articles) >= count:
                        break

        return articles

    except Exception as e:
        print(f"BBC null: {e}")
        return [{"title": "unableto  fetch  articles", "link": ""}]


def extract_article_content(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        site_selectors = []
        if "reuters.com" in url:
            site_selectors = [
                ("div", {"data-testid": "ArticleBody"}),
                ("div", {"class": "StandardArticleBody_body"}),
            ]
        elif "bbc.com" in url:
            site_selectors = [
                ("div", {"data-component": "text-block"}),
                ("div", {"class": "story-body"}),
            ]

        return extract_with_fallback(soup, site_selectors=site_selectors, url=url)

    except Exception as e:
        return f"Error extracting content: {e}"


def get_tech_articles(count=3):
    url = "https://techcrunch.com/latest/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    article_links = soup.find_all("a", class_="post-block__title__link")

    for link in article_links:
        title = link.get_text(strip=True)
        href = link["href"]
        
        if article_cache.is_article_processed(href, title):
            print(f"Skipping previously processed article: {title}")
            continue
            
        articles.append({"title": title, "link": href})
        article_cache.add_article(href, title)
        if len(articles) >= count:
            break
    return articles


def extract_tech_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        site_selectors = [
            ("div", {"class": "article-content"}),
            ("div", {"class": "entry-content"}),
        ]
        return extract_with_fallback(soup, site_selectors=site_selectors, url=url)

    except Exception as e:
        return f"Error: {e}"


def get_sports_articles(count=3):
    url = "https://www.espn.com/sports/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    article_links = soup.find_all("a", href=True)

    for link in article_links:
        href = link["href"]
        title_elem = link.find("h3") or link.find("h2") or link.find("span")
        if title_elem and "/story/" in href:
            title = title_elem.get_text(strip=True)
            full_url = href if href.startswith("http") else "https://www.espn.com" + href
            
            if article_cache.is_article_processed(full_url, title):
                print(f"Skipping previously processed article: {title}")
                continue
                
            articles.append({"title": title, "link": full_url})
            article_cache.add_article(full_url, title)
            if len(articles) >= count:
                break
    return articles


def extract_sports_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        site_selectors = [
            ("div", {"class": "story-body"}),
            ("div", {"class": "article-body"}),
        ]
        return extract_with_fallback(soup, site_selectors=site_selectors, url=url)

    except Exception as e:
        return f"Error: {e}"


def get_health_articles(count=3):
    url = "https://www.healthline.com/health-news"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    article_links = soup.find_all("a", href=True)

    for link in article_links:
        href = link["href"]
        title_elem = link.find("h2") or link.find("h3")
        if title_elem and "/health-news/" in href:
            title = title_elem.get_text(strip=True)
            full_url = href if href.startswith("http") else "https://www.healthline.com" + href
            
            if article_cache.is_article_processed(full_url, title):
                print(f"Skipping previously processed article: {title}")
                continue
                
            articles.append({"title": title, "link": full_url})
            article_cache.add_article(full_url, title)
            if len(articles) >= count:
                break
    return articles


def extract_health_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        site_selectors = [
            ("div", {"class": "article-body"}),
            ("div", {"class": "content"}),
        ]
        return extract_with_fallback(soup, site_selectors=site_selectors, url=url)

    except Exception as e:
        return f"Error: {e}"


def get_entertainment_articles(count=3):
    url = "https://variety.com/latest/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    article_links = soup.find_all("a", href=True)

    for link in article_links:
        href = link["href"]
        title_elem = link.find("h3") or link.find("h2")
        if title_elem and "variety.com" in href and "/news/" in href:
            title = title_elem.get_text(strip=True)
            
            if article_cache.is_article_processed(href, title):
                print(f"Skipping previously processed article: {title}")
                continue
                
            articles.append({"title": title, "link": href})
            article_cache.add_article(href, title)
            if len(articles) >= count:
                break
    return articles


def get_stuff():
    processed_articles = set()

    html = requests.get("https://idrw.org/")
    soup = BeautifulSoup(html.text, "html.parser")
    articles = soup.find_all("article")

    for i, article in enumerate(articles):
        heading = article.find("h2")
        if not heading:
            continue

        heading_text = heading.text.strip()
        article_text = article.text.strip()

        if heading_text in processed_articles:
            continue
        processed_articles.add(heading_text)

        print(f"\nScraped heading {i + 1}: {heading_text}")
        print(f"Scraped content: {article_text}\n")

    for i, article in enumerate(articles):
        heading = article.find("h2")
        if not heading:
            continue

        heading_text = heading.text.strip()
        article_text = article.text.strip()

        if heading_text in processed_articles:
            continue
        processed_articles.add(heading_text)

        print(f"\nScraped heading {i + 1}: {heading_text}")
        print(f"Scraped content: {article_text}\n")


def fetch_comments_continuously(post_url, service: RedditService = None):
    service = service or reddit_service
    all_comments = []
    comment_count = 0
    batch_size = 10

    print("\nfetching comments")
    print("ctrl+c to jump to the summarise part \n")

    try:
        while True:
            print(f" fetching comments {comment_count // batch_size + 1}...")

            result = service.fetch_comments(post_url, max_comments=batch_size + comment_count)

            if not result.ok:
                print(f" could not fetch comments: {result.error}")
                break

            if not result.data:
                print(" no comments there.")
                break

            new_comments = result.data[comment_count:]
            if not new_comments:
                print(" no comments found.")
                break

            all_comments.extend(new_comments)
            comment_count = len(all_comments)

            print(f" got {len(new_comments)} new comments (total num: {comment_count})")
            for comment in new_comments[-3:]:
                print(f" {comment.format()[:400]}...")

            time.sleep(2)

    except KeyboardInterrupt:
        print(f"\n fetch interrupted num of comments collected: {len(all_comments)}")

    return '\n\n'.join(comment.format() for comment in all_comments) if all_comments else "no comments available"


def analyze_with_llm(title, content):
    if content.startswith("Error :") or len(content.split()) < 30:
        return "low content. skipping"
    try:
        response: ChatResponse = chat(model='llama3.2', messages=[
            {
                'role': 'system',
                'content': """You are a global news analyst. Given a news article, respond with the following format:
                 1. Summary: ... 
                 2. Sentiment: Positive / Negative / Neutral 
                 3. Socio-economic Impact: ... 
                 4. Political Impact: ... 
                 5. Stock Market Impact: ... """,
            },
            {
                'role': 'user',
                'content': f"Title: {title}\n\nContent:\n{content}",
            },
        ])
        return response.message.content
    except Exception as e:
        return f"  Error: {e}"


def analyze_reddit_discussion(title, combined_content):
    if combined_content.startswith("Error :") or len(combined_content.split()) < 50:
        return "Insufficient content for analysis. Skipping."

    try:
        response: ChatResponse = chat(model='llama3.2', messages=[
            {
                'role': 'system',
                'content': """You are a Reddit discussion analyst powered by Llama3.2. Analyze Reddit posts and their comments to provide comprehensive insights. Structure your response with:

1. DISCUSSION SUMMARY: Brief overview of the main post and key discussion points
2. KEY THEMES: Main topics and themes discussed in comments
3. COMMUNITY SENTIMENT: Overall sentiment and emotional tone of the discussion
4. HOT TAKES: Most upvoted or controversial viewpoints
5. INSIGHTS: Deeper analysis of what this discussion reveals about the topic/community
6. ENGAGEMENT PATTERNS: How users are interacting and what drives engagement
7. TAKEAWAYS: Key conclusions and implications

Be concise but thorough, focusing on the most interesting and relevant aspects of the discussion.""",
            },
            {
                'role': 'user',
                'content': f"Reddit Post Title: {title}\n\nContent and Comments:\n{combined_content}",
            },
        ])
        return response.message.content
    except Exception as e:
        return f"Analysis Error: {e}"


def get_stuff():
    processed_articles = set()

    html = requests.get("https://idrw.org/")
    soup = BeautifulSoup(html.text, "html.parser")
    articles = soup.find_all("article")

    for i, article in enumerate(articles):
        heading = article.find("h2")
        if not heading:
            continue

        heading_text = heading.text.strip()
        article_text = article.text.strip()

        if heading_text in processed_articles:
            continue
        processed_articles.add(heading_text)

        print(f"\nScraped heading {i + 1}: {heading_text}")
        print(f"Scraped content: {article_text}\n")

        next_para = heading.find_next("p")
        if next_para:
            print(f"Preview of next: {next_para.text.strip()}")
        else:
            print("End reached.")

        try:
            response: ChatResponse = chat(model='llama3.2', messages=[
                {
                    'role': 'system',
                    'content': """summarize the defence article and provide
                     insights on its impact on the present state of global politics
                     and any future impacts it can have on INDIA
        """,
                },
                {
                    'role': 'user',
                    'content': f"Here is the news article:\n\n{article_text}",
                },
            ])

            print("\n--- LLM Response ---\n")
            print(response.message.content)
            print("\n--------------------\n")
        except Exception as e:
            print(f"dunno what happened: {e}")


def run_reddit_flow(query: str, count: int = 1, service: RedditService = None) -> None:
    service = service or reddit_service

    print(f"fetching Reddit posts for '{query}'...")
    result = service.fetch_posts(query, count=count)

    if not result.ok:
        print(f"Could not fetch Reddit posts: {result.error}")
        return

    posts = result.data
    if not posts:
        print("no posts found")
        return

    print(f"Found {len(posts)} Reddit posts.")
    posts = posts[:count]
    print(f" {len(posts)} reddit posts:")

    for i, post in enumerate(posts, 1):
        print(f"\n🔹 [{i}] {post.title}")
        print(f"🔗 {post.link}")

        content = extract_reddit_content(post)
        print(f"\n post preview:\n{content[:500]}...\n")

        print("\n  comments fetching...")
        all_comments = fetch_comments_continuously(post.link, service=service)

        combined_content = f" CONTENT:\n{content}\n\nCOMMENTS:\n{all_comments}"

        print(f"\n analysis of post and comments...")
        analysis = analyze_reddit_discussion(post.title, combined_content)
        print(f"\n  Analysis:\n{analysis}\n")

        print("------------------------------\n")


def main():
    print("Select content type to scrape and summarize:")
    print("1. Business  ")
    print("2. Technology [wip]")
    print("3. Sports  ")
    print("4. Health  ")
    print("5. DEFENCE ")
    print("6. Reddit [work in progress]")

    choice = input("Enter your choice (1-6): ").strip()

    if choice == "1":
        print("fetching  Business  articles...")
        articles = get_article_links()
        extract_func = extract_article_content
    elif choice == "2":
        print("fetching  Technology  articles...")
        articles = get_tech_articles()
        extract_func = extract_tech_content
    elif choice == "3":
        print(" fetching  Sports  articles...")
        articles = get_sports_articles()
        extract_func = extract_sports_content
    elif choice == "4":
        print("fetching  Health  articles...")
        articles = get_health_articles()
        extract_func = extract_health_content
    elif choice == "5":
        get_stuff()
        return
    elif choice == "6":
        query = input("Enter the topic you want to search on Reddit: ")
        run_reddit_flow(query, count=1)
        return

    else:
        print("Invalid choice. default is business..")
        articles = get_article_links(count=1)
        extract_func = extract_article_content

    if not articles:
        print("No articles found.")
        return

    for i, article in enumerate(articles, 1):
        print(f"\n🔹 [{i}] {article['title']}")
        print(f"🔗 {article['link']}")

        content = extract_func(article["link"])

        print(f"\n preview:\n{content[:1000]}...\n")

        analysis = analyze_with_llm(article["title"], content)
        print(f" analysis:\n{analysis}\n")

        print("------------------------------\n")
        time.sleep(1)


def parse_args():
    parser = argparse.ArgumentParser(description="Scrape and summarize news articles.")
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Flush the stored article cache file and exit."
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.clear_cache:
        article_cache.clear_cache()
    else:
        main()
