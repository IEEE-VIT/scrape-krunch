# 📰 News Analyzer with LLM Summarization

This project scrapes the latest news articles from various domains like **Business**, **Technology**, **Health**, **Sports**, **Entertainment**, and even **Reddit posts**—then feeds them into a locally running **LLM (via Ollama)** to generate a detailed analysis.

## 🚀 Features

- 🔍 Scrapes latest headlines from:
  - [Business Today](https://www.businesstoday.in)
  - [TechCrunch](https://techcrunch.com)
  - [ESPN](https://espn.com)
  - [Healthline](https://www.healthline.com)
  - [Variety](https://variety.com)
  - Reddit (via Reddit's JSON API)

- 💬 Uses **Ollama + LLaMA 3** locally for:
  - Summarization  
  - Sentiment analysis  
  - Socio-economic, political & stock market impact evaluation

- ⚙️ Clean command-line interface for selecting the type of news  
- ⏱️ Supports rate limiting with `time.sleep()`  
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
- Model (e.g., `llama3.2`) pulled via `ollama run llama3`

Install Python dependencies:
pip install requests beautifulsoup4


## ▶️ How to Run

1. Make sure Ollama is installed and running:  
   `ollama run llama3`

2. Install required Python packages:  
   `pip install requests beautifulsoup4`

3. Run the script:  

4. Follow the prompt to choose a category (1–6) and get LLM-based analysis.

## Future Scope
1. Cloud Deployment
2. Cache Previous articles
4. Buy/Sell/Hold sentiment catagories based on NIFTY50 and S&P500 using financial news data.
5. Add tickers manually or let users input a company name for financial news. 

