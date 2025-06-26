# 📰 LLM-Powered News Analyzer

This Python script scrapes the latest news articles and uses a locally running LLM (via [Ollama](https://ollama.com)) to provide insightful summaries, sentiment analysis, and potential global impacts of each article.

---

## 🔍 Features

- ✅ Web scraping using `requests` and `BeautifulSoup`
- ✅ Summarization of news articles using a local LLM
- ✅ Sentiment analysis of each article
- ✅ Socio-economic, political, and stock market impact predictions
- ✅ Automatically avoids duplicates and includes a delay to prevent IP bans

---

## 🧠 Example Output

```text
Scraped heading 1: India test-fires Agni-V missile

Scraped content: India successfully test-fired the nuclear-capable Agni-V missile...

--- LLM Response ---

1. Summary: India conducted a successful test of the Agni-V nuclear-capable ballistic missile, marking a strategic milestone.
2. Sentiment: Positive
3. Socio-economic Impact: Boosts defense R&D and indigenous capabilities.
4. Political Impact: Reinforces India's strategic posture in Asia-Pacific.
5. Stock Market Impact: May positively influence defense sector stocks.
