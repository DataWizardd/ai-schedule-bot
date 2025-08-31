from openai import OpenAI
from typing import Dict, Any, List, Optional

class AIClient:
    def __init__(self, api_key: Optional[str]):
        if not api_key:
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)

    def available(self) -> bool:
        return self.client is not None

    def json_response(self, model: str, system: str, user: str, max_tokens: int = 600, temperature: float = 0.3) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("OpenAI API key not configured.")
        resp = self.client.chat.completions.create(
            model=model,                 # 예: "gpt-4o-mini"
            temperature=temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            max_tokens=max_tokens
        )
        content = resp.choices[0].message.content
        return {} if not content else __import__("json").loads(content)
