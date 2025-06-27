import requests
from bs4 import BeautifulSoup as bs
import time
from ollama import chat
from ollama import ChatResponse
from duckduckgo_search import DDGS


def get_stuff():
    processed_articles = set()


    
    html = requests.get("https://idrw.org/") 
    # incorporate userinput here which is then feeded to the browser
    
    soup = bs(html.text, "html.parser")  
    articles = soup.find_all("article")
    
    for i, article in enumerate(articles):
        # find heading
        heading = article.find("h2")
        if not heading:
            continue
            
        heading_text = heading.text.strip()
        article_text = article.text.strip()
        
        
        # if content_hash in processed_articles:
        #     print(f": {heading_text[:50]}...")
        #     continue
            
        # Add to processed set
        
        print(f"scraped heading  {i+1}: {heading_text}\n")
        print(f"scraped content: {article_text}...\n")
        
        next_para = heading.find_next("p")
        if next_para:
            print(f"moving on to the next one: {next_para.text.strip()}")
        else:
            print("end reached")
        
        
        try:
                response: ChatResponse = chat(model='llama3.2', messages=[
                    {
                        'role': 'user',
                        'content': f"Summarize this  and also give your thoughts on this : {article_text}",
                    },
                ])
                
                print("\n\n\n\n\n")
                print("summary:")
                print(response.message.content)
                print("\n\n\n\n\n\n")
                
        except Exception as e:
                print(f"dunno what happened: {e}")    
        
        
        
        # optional delay to avoid ip block
        # time.sleep(1)


def search_duckduckgo(query, max_results=10):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
        return results

results = search_duckduckgo(input("Enter your search query: "), max_results=5)
for result in results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['href']}")
    print(f"Body: {result['body']}")
    print("----------")
    response: ChatResponse = chat(model='llama3.2', messages=[
                    {
                        'role': 'user',
                        'content': f"Summarize this  and also give your thoughts on this : {result['body']}",
                    },
                ])
                
    print("\n\n\n\n\n")
    print("summary:")
    print(response.message.content)
    print("\n\n\n\n\n\n")


# if __name__ == "__main__":
    # get_stuff()

