# import requests
# from bs4 import BeautifulSoup
# from ollama import chat, ChatResponse
# import time
# from duckduckgo_search import DDGS as ddgs


# def search_duckduckgo(query, max_results=10):
#     with ddgs() as ddgs_instance:
#         reddit_results = list(ddgs_instance.text(keywords=query, max_results=max_results))
#     return reddit_results

# BASE_URL = "https://www.businesstoday.in"

# def get_article_links(count=5):
#     url = f"{BASE_URL}/latest"
#     headers = {"User-Agent": "Mozilla/5.0"}
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.text, "html.parser")
    
#     anchors = soup.find_all("a", href=True, title=True)
#     articles = []
    
#     for tag in anchors:
#         href = tag["href"]
#         title = tag["title"].strip()
#         if "/story/" in href:
#             full_url = href if href.startswith("http") else BASE_URL + href
#             articles.append({"title": title, "link": full_url})
#             if len(articles) >= count:
#                 break
#     return articles

# def extract_article_content(url):
#     headers = {"User-Agent": "Mozilla/5.0"}
#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         soup = BeautifulSoup(response.text, "html.parser")
        
#         article_div = soup.find("div", class_="text-formatted field--name-body")
#         if not article_div:
#             article_divs = soup.find_all("div", class_=lambda x: x and "field--name-body" in x)
#             article_div = article_divs[0] if article_divs else None
        
#         if article_div:
#             paragraphs = article_div.find_all("p")
#             content = "\n".join(p.get_text(strip=True) for p in paragraphs)
#             return content.strip() if content else "Empty  body."
#         else:
#             return " article div not found."
    
#     except Exception as e:
#         return f"Error : {e}"

# def get_tech_articles(count=5):
#     url = "https://techcrunch.com/latest/"
#     headers = {"User-Agent": "Mozilla/5.0"}
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.text, "html.parser")
    
#     articles = []
#     article_links = soup.find_all("a", class_="post-block__title__link")
    
#     for link in article_links:
#         title = link.get_text(strip=True)
#         href = link["href"]
#         articles.append({"title": title, "link": href})
#         if len(articles) >= count:
#             break
#     return articles

# def extract_tech_content(url):
#     headers = {"User-Agent": "Mozilla/5.0"}
#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         soup = BeautifulSoup(response.text, "html.parser")
        
#         article_div = soup.find("div", class_="article-content")
#         if not article_div:
#             article_div = soup.find("div", class_="entry-content")
        
#         if article_div:
#             paragraphs = article_div.find_all("p")
#             content = "\n".join(p.get_text(strip=True) for p in paragraphs)
#             return content.strip() if content else "Empty content."
#         else:
#             return "Content div not found."
    
#     except Exception as e:
#         return f"Error: {e}"

# def get_sports_articles(count=5):
#     url = "https://www.espn.com/sports/"
#     headers = {"User-Agent": "Mozilla/5.0"}
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.text, "html.parser")
    
#     articles = []
#     article_links = soup.find_all("a", href=True)
    
#     for link in article_links:
#         href = link["href"]
#         title_elem = link.find("h3") or link.find("h2") or link.find("span")
#         if title_elem and "/story/" in href:
#             title = title_elem.get_text(strip=True)
#             full_url = href if href.startswith("http") else "https://www.espn.com" + href
#             articles.append({"title": title, "link": full_url})
#             if len(articles) >= count:
#                 break
#     return articles

# def extract_sports_content(url):
#     headers = {"User-Agent": "Mozilla/5.0"}
#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         soup = BeautifulSoup(response.text, "html.parser")
        
#         article_div = soup.find("div", class_="story-body") or soup.find("div", class_="article-body")
        
#         if article_div:
#             paragraphs = article_div.find_all("p")
#             content = "\n".join(p.get_text(strip=True) for p in paragraphs)
#             return content.strip() if content else "Empty content."
#         else:
#             return "Content div not found."
    
#     except Exception as e:
#         return f"Error: {e}"

# def get_health_articles(count=5):
#     url = "https://www.healthline.com/news"
#     headers = {"User-Agent": "Mozilla/5.0"}
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.text, "html.parser")
    
#     articles = []
#     article_links = soup.find_all("a", href=True)
    
#     for link in article_links:
#         href = link["href"]
#         title_elem = link.find("h2") or link.find("h3")
#         if title_elem and "/health-news/" in href:
#             title = title_elem.get_text(strip=True)
#             full_url = href if href.startswith("http") else "https://www.healthline.com" + href
#             articles.append({"title": title, "link": full_url})
#             if len(articles) >= count:
#                 break
#     return articles

# def extract_health_content(url):
#     headers = {"User-Agent": "Mozilla/5.0"}
#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         soup = BeautifulSoup(response.text, "html.parser")
        
#         article_div = soup.find("div", class_="article-body") or soup.find("div", class_="content")
        
#         if article_div:
#             paragraphs = article_div.find_all("p")
#             content = "\n".join(p.get_text(strip=True) for p in paragraphs)
#             return content.strip() if content else "Empty content."
#         else:
#             return "Content div not found."
    
#     except Exception as e:
#         return f"Error: {e}"

# def get_entertainment_articles(count=5):
#     url = "https://variety.com/latest/"
#     headers = {"User-Agent": "Mozilla/5.0"}
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.text, "html.parser")
    
#     articles = []
#     article_links = soup.find_all("a", href=True)
    
#     for link in article_links:
#         href = link["href"]
#         title_elem = link.find("h3") or link.find("h2")
#         if title_elem and "variety.com" in href and "/news/" in href:
#             title = title_elem.get_text(strip=True)
#             articles.append({"title": title, "link": href})
#             if len(articles) >= count:
#                 break
#     return articles

# def extract_entertainment_content(url):
#     headers = {"User-Agent": "Mozilla/5.0"}
#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         soup = BeautifulSoup(response.text, "html.parser")
        
#         article_div = soup.find("div", class_="pmc-paywall") or soup.find("div", class_="article-wrap")
        
#         if article_div:
#             paragraphs = article_div.find_all("p")
#             content = "\n".join(p.get_text(strip=True) for p in paragraphs)
#             return content.strip() if content else "Empty content."
#         else:
#             return "Content div not found."
    
#     except Exception as e:
#         return f"Error: {e}"

# def get_reddit_posts(query, count=5):
#     search_url = f"https://www.reddit.com/search.json?q={query}&sort=hot&limit={count}"
#     headers = {"User-Agent": "Mozilla/5.0"}
    
#     try:
#         response = requests.get(search_url, headers=headers)
#         data = response.json()
        
#         posts = []
#         for post in data['data']['children']:
#             post_data = post['data']
#             title = post_data['title']
#             selftext = post_data.get('selftext', '')
#             url = f"https://www.reddit.com{post_data['permalink']}"
#             subreddit = post_data['subreddit']
#             score = post_data['score']
            
#             posts.append({
#                 'title': f"[r/{subreddit}] {title}",
#                 'link': url,
#                 'content': selftext,
#                 'score': score
#             })
        
#         return posts
#     except Exception as e:
#         return [{"title": f"Error fetching Reddit posts: {e}", "link": "", "content": "", "score": 0}]

# def extract_reddit_content(post):
#     return post['content'] if post['content'] else "No text content available."

# def analyze_with_llm(title, content):
#     if content.startswith("Error :") or len(content.split()) < 30:
#         return "low content. skipping"
#     try:
#         response: ChatResponse = chat(model='llama3.2', messages=[
#             {
#                 'role': 'system',
#                 'content': """You are a global news analyst. Given a news article, respond with the following format: 1. Summary: ... 2. Sentiment: Positive / Negative / Neutral 3. Socio-economic Impact: ... 4. Political Impact: ... 5. Stock Market Impact: ... """,
#             },
#             {
#                 'role': 'user',
#                 'content': f"Title: {title}\n\nContent:\n{content}",
#             },
#         ])
#         return response.message.content
#     except Exception as e:
#         return f"  Error: {e}"

# def main():
#     print("Select content type to scrape and summarize:")
#     print("1. Business  ")
#     print("2. Technology  (")
#     print("3. Sports  ")
#     print("4. Health  ")
#     print("5. Entertainment ")
#     print("6. Reddit [work in progress]")
    
#     choice = input("Enter your choice (1-6): ").strip()
    
#     if choice == "1":
#         print("🔍 fetching  Business  articles...")
#         articles = get_article_links(count=5)
#         extract_func = extract_article_content
#         analyze_with_llm
#     elif choice == "2":
#         print("🔍 fetching  Technology  articles...")
#         articles = get_tech_articles(count=5)
#         extract_func = extract_tech_content
#     elif choice == "3":
#         print("🔍 fetching  Sports  articles...")
#         articles = get_sports_articles(count=5)
#         extract_func = extract_sports_content
#     elif choice == "4":
#         print("🔍 fetching  Health  articles...")
#         articles = get_health_articles(count=5)
#         extract_func = extract_health_content
#     elif choice == "5":
#         print("🔍 fetching  Entertainment   articles...")
#         articles = get_entertainment_articles(count=5)
#         extract_func = extract_entertainment_content
#     elif choice == "6":
#         # reddit_results = search_duckduckgo(input("give the topic you want to search on reddit  "), max_results=5)
#         # for result in reddit_results:
#         #     print(f"Title: {result['title']}")
#         #     print(f"URL: {result['href']}")
#         #     print(f"Body: {result['body']}")
#         #     print("----------")
#         #     response: ChatResponse = chat(model='llama3.2', messages=[
#         #                     {
#         #                         'role': 'user',
#         #                         'content': f"Summarize this  reddit thread omit any foul language and give to the point answers  and do not start with heres a summary of the thread instead just give the content : {result['body']}",
#         #                     },
#         #                 ])
                        
#         #     print("\n\n\n\n\n")
#         #     print("summary:")
#         #     print(response.message.content)
#         #     print("\n\n\n\n\n\n")
#         get_reddit_posts_query = input("Enter the topic you want to search on Reddit: ")
#         print(f"🔍 fetching Reddit posts for '{get_reddit_posts_query}'...")
#         articles = get_reddit_posts(get_reddit_posts_query, count=5)
#         extract_func = extract_reddit_content
#         if not articles:
#             print("no posted found ")
#             return
#         print(f"Found {len(articles)} Reddit posts.")
#         if len(articles) < 5:
#             print("limited postes avaliable")
#             count = len(articles)
#         else:
#             count = 5
#         articles = articles[:count]
#         print(f"Displaying {count} Reddit posts:")  
#         print(articles[2]['content'])
#         for i in range(4):
#             print(f"\n🔹 [{i+1}] {articles[i]['title']}")
#             print(f"🔗 {articles[i]['link']}")
            
#             content = extract_func(articles[i])
            
#             print(f"\n Preview:\n{content[:1000]}...\n")
            
#             analysis = analyze_with_llm(articles[i]["title"], content)
#             print(f" Analysis:\n{analysis}\n")
            
#             print("------------------------------\n")

#         response: ChatResponse = chat(model='llama3.2', messages=[
                           
#                             {
#                                 'role': 'user',
#                                 'content': f"Summarize this  reddit thread omit any foul language and give to the point answers  and do not start with heres a summary of the thread instead just give the content : {articles[i]['content']}",
#                             },
#                         ])
                        
#         print("\n\n\n\n\n")
#         print("summary:")
#         print(response.message.content)
#         print("\n\n\n\n\n\n")

#     else:
#         print("Invalid choice. Defaulting to Business News...")
#         articles = get_article_links(count=5)
#         extract_func = extract_article_content
    

#     for i, article in enumerate(articles, 1):
#         print(f"\n🔹 [{i}] {article['title']}")
#         print(f"🔗 {article['link']}")
        
#         content = extract_func(article["link"])
        
#         print(f"\n Preview:\n{content[:1000]}...\n")
        
#         analysis = analyze_with_llm(article["title"], content)
#         print(f" Analysis:\n{analysis}\n")
        
#         print("------------------------------\n")
#         time.sleep(1)

# if __name__ == "__main__":
#     main()



import requests
from bs4 import BeautifulSoup
from ollama import chat, ChatResponse
import time
from duckduckgo_search import DDGS as ddgs


def search_duckduckgo(query, max_results=10):
    with ddgs() as ddgs_instance:
        reddit_results = list(ddgs_instance.text(keywords=query, max_results=max_results))
    return reddit_results

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
        
        article_div = soup.find("div", class_="text-formatted field--name-body")
        if not article_div:
            article_divs = soup.find_all("div", class_=lambda x: x and "field--name-body" in x)
            article_div = article_divs[0] if article_divs else None
        
        if article_div:
            paragraphs = article_div.find_all("p")
            content = "\n".join(p.get_text(strip=True) for p in paragraphs)
            return content.strip() if content else "Empty  body."
        else:
            return " article div not found."
    
    except Exception as e:
        return f"Error : {e}"

def get_tech_articles(count=5):
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

def get_sports_articles(count=5):
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

def get_health_articles(count=5):
    url = "https://www.healthline.com/news"
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

def get_entertainment_articles(count=5):
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

def extract_entertainment_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        article_div = soup.find("div", class_="pmc-paywall") or soup.find("div", class_="article-wrap")
        
        if article_div:
            paragraphs = article_div.find_all("p")
            content = "\n".join(p.get_text(strip=True) for p in paragraphs)
            return content.strip() if content else "Empty content."
        else:
            return "Content div not found."
    
    except Exception as e:
        return f"Error: {e}"

def get_reddit_posts(query, count=5):
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
    return post['content'] if post['content'] else "No text content available."

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

def main():
    print(" content type to scrape and summarize:")
    print("1. Business  ")
    print("2. Technology  ")
    print("3. Sports  ")
    print("4. Health  ")
    print("5. Entertainment ")
    print("6. Reddit [work in progress]")
    
    choice = input(" your choice (1-6): ").strip()
    
    if choice == "1":
        print("🔍 fetching  Business  articles...")
        articles = get_article_links(count=5)
        extract_func = extract_article_content
    elif choice == "2":
        print("🔍 fetching  Technology  articles...")
        articles = get_tech_articles(count=5)
        extract_func = extract_tech_content
    elif choice == "3":
        print("🔍 fetching  Sports  articles...")
        articles = get_sports_articles(count=5)
        extract_func = extract_sports_content
    elif choice == "4":
        print("🔍 fetching  Health  articles...")
        articles = get_health_articles(count=5)
        extract_func = extract_health_content
    elif choice == "5":
        print("🔍 fetching  Entertainment   articles...")
        articles = get_entertainment_articles(count=5)
        extract_func = extract_entertainment_content
    elif choice == "6":
        get_reddit_posts_query = input("Enter the topic you want to search on Reddit: ")
        print(f"🔍 fetching Reddit posts for '{get_reddit_posts_query}'...")
        articles = get_reddit_posts(get_reddit_posts_query, count=5)
        extract_func = extract_reddit_content
        
        if not articles:
            print("no posted found ")
            return
        
        print(f"Found {len(articles)} Reddit posts.")
        if len(articles) < 5:
            print("limited postes avaliable")
            count = len(articles)
        else:
            count = 5
        
        articles = articles[:count]
        print(f"Displaying {count} Reddit posts:")
        
        for i in range(count):
            print(f"\n🔹 [{i+1}] {articles[i]['title']}")
            print(f"🔗 {articles[i]['link']}")
            
            content = extract_func(articles[i])
            
            print(f"\n Preview:\n{content[:1000]}...\n")
            
            analysis = analyze_with_llm(articles[i]["title"], content)
            print(f" Analysis:\n{analysis}\n")
            
            print("------------------------------\n")
        
        return
    else:
        print("Invalid choice. Defaulting to Business News...")
        articles = get_article_links(count=5)
        extract_func = extract_article_content
    
    if not articles:
        print("No articles found.")
        return

    for i, article in enumerate(articles, 1):
        print(f"\n🔹 [{i}] {article['title']}")
        print(f"🔗 {article['link']}")
        
        content = extract_func(article["link"])
        
        print(f"\n Preview:\n{content[:1000]}...\n")
        
        analysis = analyze_with_llm(article["title"], content)
        print(f" Analysis:\n{analysis}\n")
        
        print("------------------------------\n")
        time.sleep(1)

if __name__ == "__main__":
    main()