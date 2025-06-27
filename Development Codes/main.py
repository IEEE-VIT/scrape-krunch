import time
from scraper import NewsScraper
from llm_analyzer import NewsLLMAnalyzer

def main():
    scraper = NewsScraper()
    analyzer = NewsLLMAnalyzer()

    print("🔍 Scraping latest Business Today articles...")
    articles = scraper.get_article_links(count=5)

    for i, article in enumerate(articles, 1):
        print(f"\n🔹 [{i}] {article['title']}")
        print(f"🔗 {article['link']}")

        content = scraper.extract_article_content(article["link"])
        print(f"\n📝 Content Preview:\n{content[:500]}...\n")

        analysis = analyzer.analyze(article["title"], content)
        print(f"🤖 LLM Analysis:\n{analysis}\n")

        print("-----------------------------------------------------\n")
        time.sleep(1)

if __name__ == "__main__":
    main()
