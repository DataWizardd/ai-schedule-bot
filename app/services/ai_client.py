# app/services/ai_client.py
from typing import Optional, List, Dict, Any
from openai import OpenAI

class AIClient:
    def __init__(self, key: Optional[str]):
        self.available = bool(key)
        self.client = OpenAI(api_key=key) if self.available else None

    def chat(self, messages: List[Dict[str, str]], model: str = "gpt-4o-mini",
             temperature: float = 0.2, max_tokens: int = 600):
        if not self.available:
            return None
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
