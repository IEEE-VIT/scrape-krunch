from ollama import chat, ChatResponse

class NewsLLMAnalyzer:
    def __init__(self, model_name='llama3.2'):
        self.model = model_name
        self.system_prompt = """You are a global news analyst.
Given a news article, respond with the following format:
1. Summary: ...
2. Sentiment: Positive / Negative / Neutral
3. Socio-economic Impact: ...
4. Political Impact: ...
5. Stock Market Impact: ...
"""

    def analyze(self, title: str, content: str) -> str:
        if content.startswith("❌") or len(content.split()) < 30:
            return "⚠️ Skipping due to low content."
        try:
            response: ChatResponse = chat(model=self.model, messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Title: {title}\n\nContent:\n{content}"},
            ])
            return response.message.content
        except Exception as e:
            return f"❌ LLM Error: {e}"
