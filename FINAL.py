import requests
from bs4 import BeautifulSoup
from ollama import chat, ChatResponse
import time
from duckduckgo_search import DDGS as ddgs

def search_duckduckgo(query, max_results=10):
    with ddgs() as ddgs_instance:
        reddit_results = list(ddgs_instance.text(keywords=query, max_results=max_results))
    return reddit_results

def get_article_links(count=1):
    try:
        query = "latest buissness news 2025"
        print(f"biz articles getting..")
        
        results = search_duckduckgo(query, max_results=count * 2)
        articles = []
        
        for result in results[:count]:
            if result.get('title') and result.get('href'):
                url = result['href']
                if any(source in url.lower() for source in ['reuters', 'bloomberg', 'wsj', 'marketwatch', 'cnbc', 'yahoo', 'finance']):
                    articles.append({
                        "title": result['title'],
                        "link": url
                    })
                    if len(articles) >= count:
                        break
        
        if not articles:
            for result in results[:count]:
                if result.get('title') and result.get('href'):
                    articles.append({
                        "title": result['title'],
                        "link": result['href']
                    })
                    if len(articles) >= count:
                        break
        
        return articles if articles else get_fallback_business_news(count)
    
    except Exception as e:
        print(f" search failed: {e}. fallback...")
        return get_fallback_business_news(count)

def get_fallback_business_news(count=1):
    return [{
        "title": "Business News: Global Markets Show Mixed Performance Amid Economic Uncertainty",
        "link": "https://example.com/business-news"
    }]

def get_bbc_business_articles(count=1):
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
                    articles.append({"title": title, "link": full_url})
                    
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
        
        if "reuters.com" in url:
            article_div = soup.find("div", {"data-testid": "ArticleBody"}) or soup.find("div", class_="StandardArticleBody_body")
            if article_div:
                paragraphs = article_div.find_all("p")
                content = "\n".join(p.get_text(strip=True) for p in paragraphs)
                return content.strip() if content else "Empty article body."
        
        elif "bbc.com" in url:
            article_div = soup.find("div", {"data-component": "text-block"}) or soup.find("div", class_="story-body")
            if not article_div:
                article_div = soup.find("article") or soup.find("main")
            
            if article_div:
                paragraphs = article_div.find_all("p")
                content = "\n".join(p.get_text(strip=True) for p in paragraphs)
                return content.strip() if content else "Empty article body."
        
        paragraphs = soup.find_all("p")
        if paragraphs:
            content = "\n".join(p.get_text(strip=True) for p in paragraphs[:10])  # First 10 paragraphs
            return content.strip() if content else "Could not extract content."
        
        return "Article content div not found."
    
    except Exception as e:
        return f"Error extracting content: {e}"

def get_tech_articles(count=1):
    url = "https://techcrunch.com/latest/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    articles = []
    article_links = soup.find_all("a", class_="post-block__title__link")
    
    for link in article_links:
        title = link.get_text(strip=True)
        href = link["href"]
        articles.append({"title": title, "link": href})
        if len(articles) >= count:
            break
    return articles

def extract_tech_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        article_div = soup.find("div", class_="article-content")
        if not article_div:
            article_div = soup.find("div", class_="entry-content")
        
        if article_div:
            paragraphs = article_div.find_all("p")
            content = "\n".join(p.get_text(strip=True) for p in paragraphs)
            return content.strip() if content else "Empty content."
        else:
            return "Content div not found."
    
    except Exception as e:
        return f"Error: {e}"

def get_sports_articles(count=1):
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
            articles.append({"title": title, "link": full_url})
            if len(articles) >= count:
                break
    return articles

def extract_sports_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        article_div = soup.find("div", class_="story-body") or soup.find("div", class_="article-body")
        
        if article_div:
            paragraphs = article_div.find_all("p")
            content = "\n".join(p.get_text(strip=True) for p in paragraphs)
            return content.strip() if content else "Empty content."
        else:
            return "Content div not found."
    
    except Exception as e:
        return f"Error: {e}"

def get_health_articles(count=1):
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
            articles.append({"title": title, "link": full_url})
            if len(articles) >= count:
                break
    return articles

def extract_health_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        article_div = soup.find("div", class_="article-body") or soup.find("div", class_="content")
        
        if article_div:
            paragraphs = article_div.find_all("p")
            content = "\n".join(p.get_text(strip=True) for p in paragraphs)
            return content.strip() if content else "Empty content."
        else:
            return "Content div not found."
    
    except Exception as e:
        return f"Error: {e}"

def get_entertainment_articles(count=1):
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
            articles.append({"title": title, "link": href})
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

def get_reddit_posts(query, count=7):
    search_url = f"https://www.reddit.com/search.json?q={query}&sort=hot&limit={count}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(search_url, headers=headers)
        data = response.json()
        
        posts = []
        for post in data['data']['children']:
            post_data = post['data']
            title = post_data['title']
            selftext = post_data.get('selftext', '')
            url = f"https://www.reddit.com{post_data['permalink']}"
            subreddit = post_data['subreddit']
            score = post_data['score']
            
            posts.append({
                'title': f"[r/{subreddit}] {title}",
                'link': url,
                'content': selftext,
                'score': score
            })
        
        return posts
    except Exception as e:
        return [{"title": f"Error fetching Reddit posts: {e}", "link": "", "content": "", "score": 0}]

def extract_reddit_content(post):
    if 'content' in post:
        return post['content'] if post['content'] else "No text content available."
    else:
        return "No text content available."

def get_reddit_comments(post_url, max_comments=50):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        json_url = post_url.rstrip('/') + '.json'
        response = requests.get(json_url, headers=headers)
        data = response.json()
        
        comments = []
        if len(data) > 1 and 'data' in data[1]:
            comment_data = data[1]['data']['children']
            
            for comment in comment_data[:max_comments]:
                if comment['kind'] == 't1' and 'body' in comment['data']:
                    body = comment['data']['body']
                    author = comment['data']['author']
                    score = comment['data']['score']
                    comments.append(f"[{author}] ({score} points): {body}")
        
        return '\n\n'.join(comments) if comments else "No comments available"
    
    except Exception as e:
        return f"Error fetching comments: {e}"

def fetch_comments_continuously(post_url):
    all_comments = []
    comment_count = 0
    batch_size = 10
    
    print("\nfetching comments")
    print("ctrl+c to jump to the summarise part \n")
    
    try:
        while True:
            print(f" fetching comments {comment_count//batch_size + 1}...")
            
            comments = get_reddit_comments(post_url, max_comments=batch_size + comment_count)
            
            if comments and comments != "No comments available":
                comment_list = comments.split('\n\n')
                new_comments = comment_list[comment_count:]
                
                if new_comments:
                    all_comments.extend(new_comments)
                    comment_count = len(all_comments)
                    
                    print(f" got {len(new_comments)} new comments (total num: {comment_count})")
                    
                    for i, comment in enumerate(new_comments[-3:], 1):
                        print(f" {comment[:400]}...")
                else:
                    print(" no comments found.")
                    break
            else:
                print(" no comments there.")
                break
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print(f"\n fetch interrupted num of comments collected: {len(all_comments)}")
    
    return '\n\n'.join(all_comments) if all_comments else "no comments available"

def analyze_with_llm(title, content):
    if content.startswith("Error :") or len(content.split()) < 30:
        return "low content. skipping"
    try:
        response: ChatResponse = chat(model='llama3.2', messages=[
            {
                'role': 'system',
                'content': """You are a global news analyst. Given a news article, respond with the following format: 1. Summary: ... 2. Sentiment: Positive / Negative / Neutral 3. Socio-economic Impact: ... 4. Political Impact: ... 5. Stock Market Impact: ... """,
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
                            'content': """summarize the defence article and provide insights on its impact on the present state of global politics and any future impacts it can have on INDIA
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
        articles = get_article_links(count=1)
        extract_func = extract_article_content
    elif choice == "2":
        print("fetching  Technology  articles...")
        articles = get_tech_articles(count=1)
        extract_func = extract_tech_content
    elif choice == "3":
        print(" fetching  Sports  articles...")
        articles = get_sports_articles(count=1)
        extract_func = extract_sports_content
    elif choice == "4":
        print("fetching  Health  articles...")
        articles = get_health_articles(count=1)
        extract_func = extract_health_content
    elif choice == "5":
        get_stuff()
        return
    elif choice == "6":
        get_reddit_posts_query = input("Enter the topic you want to search on Reddit: ")
        print(f"fetching Reddit posts for '{get_reddit_posts_query}'...")
        articles = get_reddit_posts(get_reddit_posts_query, count=1)
        extract_func = extract_reddit_content
        
        if not articles:
            print("no posted found ")
            return
        
        print(f"Found {len(articles)} Reddit posts.")
        if len(articles) < 1:
            print("limited postes avaliable")
            count = len(articles)
        else:
            count = 1
        
        articles = articles[:count]
        print(f" {count} reddit posts:")
        
        for i in range(count):
            print(f"\n🔹 [{i+1}] {articles[i]['title']}")
            print(f"🔗 {articles[i]['link']}")
            
            content = extract_func(articles[i])
            
            print(f"\n post preview:\n{content[:500]}...\n")
            
            print("\n  comments fetching...")
            all_comments = fetch_comments_continuously(articles[i]['link'])
            
            combined_content = f" CONTENT:\n{content}\n\nCOMMENTS:\n{all_comments}"
            
            print(f"\n analysis of post and comments...")
            analysis = analyze_reddit_discussion(articles[i]["title"], combined_content)
            print(f"\n  Analysis:\n{analysis}\n")
            
            print("------------------------------\n")
        
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

if __name__ == "__main__":
    main()