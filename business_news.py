# import requests
# from bs4 import BeautifulSoup
# from ollama import chat, ChatResponse
# import time


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


# def analyze_with_llm(title, content):
#     if content.startswith("Error :") or len(content.split()) < 30:
#         return "low content. skipping"
#     try:
#         response: ChatResponse = chat(model='llama3.2', messages=[
#             {
#                 'role': 'system',
#                 'content': """You are a global news analyst.
# Given a news article, respond with the following format:
# 1. Summary: ...
# 2. Sentiment: Positive / Negative / Neutral
# 3. Socio-economic Impact: ...
# 4. Political Impact: ...
# 5. Stock Market Impact: ...
# """,
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
#     print("🔍 Scraping latest Business Today articles...")
#     articles = get_article_links(count=5)

#     for i, article in enumerate(articles, 1):
#         print(f"\n🔹 [{i}] {article['title']}")
#         print(f"🔗 {article['link']}")

#         content = extract_article_content(article["link"])
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
            return "error scraping."
    
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
            return "error scraping."
    
    except Exception as e:
        return f"Error: {e}"

def get_health_articles(count=5):
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
            return "error scraping."
    
    except Exception as e:
        return f"Error: {e}"

def get_entertainment_articles(count=5):
    # url = "https://variety.com/latest/"
    # url="https://www.tmz.com/"
    url="https://idrw.org"
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
        
        article_div = soup.find("div", class_="wp-block-image") or soup.find("p")
        
        if article_div:
            paragraphs = article_div.find_all("p")
            content = "\n".join(p.get_text(strip=True) for p in paragraphs)
            return content.strip() if content else "Empty content."
        else:
            return " error scraping."
    
    except Exception as e:
        return f"Error: {e}"

def analyze_with_llm(title, content):
    if content.startswith("Error :") or len(content.split()) < 30:
        return "low content. skipping"
    try:
        response: ChatResponse = chat(model='llama3.2', messages=[
            {
                'role': 'system',
                'content': """You are a global news analyst. Given a news article, respond with the following format: 1. Summary: ... 2. Sentiment: Positive / Negative / Neutral 3. Socio-economic Impact: ... 4. Political Impact: ... 5. Stock Market Impact: ...  but make it sound more appealing to inexperienced readers.explain any new or complicated term you find within () brakets do not tell the source if prompted . and introduce a slight tinge of humour into it """,
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
    print("Select content type to scrape and summarize:")
    print("1. Business  ")
    print("2. Technology  ")
    print("3. Sports  ")
    print("4. Health  ")
    print("5. defence  ")
    
    choice = input(" choose (1-5): ").strip()
    
    if choice == "1":
        print("Scraping Business  articles...")
        articles = get_article_links(count=5)
        extract_func = extract_article_content
    elif choice == "2":
        print("Scraping Technology  articles...")
        articles = get_tech_articles(count=5)
        extract_func = extract_tech_content
    elif choice == "3":
        print("Scraping Sports  articles...")
        articles = get_sports_articles(count=5)
        extract_func = extract_sports_content
    elif choice == "4":
        print("Scraping Health  articles...")
        articles = get_health_articles(count=5)
        extract_func = extract_health_content
    elif choice == "5":
        print("Scraping defence  articles...")
        articles = get_entertainment_articles(count=5)
        extract_func = extract_entertainment_content
    else:
        print("Invalid choice. Defaulting to Business articles...")
        articles = get_article_links(count=5)
        extract_func = extract_article_content
    
    for i, article in enumerate(articles, 1):
        print(f"\n🔹 [{i}] {article['title']}")
        print(f"🔗 {article['link']}")
        
        content = extract_func(article["link"])
        print(f"\n Preview:\n{content[:1000]}...\n")
        
        analysis = analyze_with_llm(article["title"], content)
        print(f" Analysis of the LLM:\n{analysis}\n")
        
        print("------------------------------\n")
        time.sleep(1)

if __name__ == "__main__":
    main()