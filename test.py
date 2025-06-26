import requests
from bs4 import BeautifulSoup as bs
import time
from ollama import chat
from ollama import ChatResponse


def get_stuff():
    processed_articles = set()

    html = requests.get("https://idrw.org/")
    soup = bs(html.text, "html.parser")
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
                    'content': f"Here is the news article:\n\n{article_text}",
                },
            ])

            print("\n--- LLM Response ---\n")
            print(response.message.content)
            print("\n--------------------\n")

        except Exception as e:
            print(f"dunno what happened: {e}")

        # optional delay to avoid ip block
        # time.sleep(1)


if __name__ == "__main__":
    get_stuff()