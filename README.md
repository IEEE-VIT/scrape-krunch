# 📰 News Analyzer with LLM Summarization

![Hacktoberfest 2025 banner](./scrape_krunch_hacktoberfest.png)

This project scrapes the latest news articles from various domains like **Business**, **Technology**, **Health**, **Sports**, **Entertainment**, and even **Reddit posts**—then feeds them into a locally running **LLM (via Ollama)** to generate a detailed analysis.

## 🚀 Features

- 🔍 Scrapes latest headlines from:
  - [Business Today](https://www.businesstoday.in)
  - [TechCrunch](https://techcrunch.com)
  - [ESPN](https://espn.com)
  - [Healthline](https://www.healthline.com)
  - [Variety](https://variety.com)
  - Reddit (via Reddit's JSON API)

- 💬 Uses **Ollama + LLaMA 3.2** locally for:
  - Summarization  
  - Sentiment analysis  
  - Socio-economic, political & stock market impact evaluation

- ⚙️ Clean command-line interface for selecting the type of news  
- ⏱️ Fetches business, technology, sports, and health article content concurrently using `asyncio` and `ThreadPoolExecutor`, with `asyncio.Semaphore(3)` limiting extraction to three requests at a time.
- 🔗 Keeps batch results in article order; failed requests are reported and skipped without stopping other articles. Each article request uses a 10-second timeout and checks HTTP status.  
- 🔗 Extracts full article content when possible  

## 🧠 LLM Prompt

The LLM receives a prompt like:

You are a global news analyst.
Given a news article, respond with the following format:

    Summary: ...

    Sentiment: Positive / Negative / Neutral

    Socio-economic Impact: ...

    Political Impact: ...

    Stock Market Impact: ...


## 📦 Requirements

- Python 3.8+
- [Ollama](https://ollama.com) installed and running
- Model (e.g., `llama3.2`) pulled via `ollama run llama3.2`

Install Python dependencies:
pip install requests beautifulsoup4


## ▶️ How to Run

1. Make sure Ollama is installed and running:  
   `ollama run llama3.2`

2. Install required Python packages:  
   `pip install requests beautifulsoup4`

3. Run the script:  

4. Follow the prompt to choose a category (1–6) and get LLM-based analysis.

## Future Scope
1. Cloud Deployment
2. Cache Previous articles
4. Buy/Sell/Hold sentiment catagories based on NIFTY50 and S&P500 using financial news data.
5. Add tickers manually or let users input a company name for financial news. 


## Robots.txt compliance

Direct article, category, defence, and Reddit HTTP requests check each origin's
`robots.txt` with `urllib.robotparser.RobotFileParser` before fetching content.
The check uses the same User-Agent sent with the request (`Mozilla/5.0` by default).
Rules are cached for the process lifetime. Disallowed URLs are skipped with an
INFO log, including redirect destinations. Blocked articles are not sent to the LLM.

`Crawl-delay` is enforced per host, including concurrent callers, starting after
the robots fetch and between subsequent requests. Different hosts can proceed
independently, with at most three transport calls active. Missing robots files
(404/410) allow scraping; inaccessible rules, other HTTP errors, or timeouts
skip that origin for the current run. Restart the application to retry its rules.

DuckDuckGo search requests are managed internally by the third-party search
library; returned article URLs pass through the robots checks above.
No additional dependencies are needed. Run the isolated policy tests with:

```bash
python -m unittest discover -s tests -v
```
