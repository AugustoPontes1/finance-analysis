import os
import json
import requests

from backend.apps.values_ai_extraction.llm.base import BaseLLMService

PROMPT = """You are a financial document analyzer.
Extract ALL label-value pairs you can find in the document below.
Labels are names of services, stores, or descriptions. Values are monetary amounts.
Return ONLY a valid JSON array, nothing else. Example:
[{{"label": "Uber", "value": "R$ 20.50"}}, {{"label": "iFood", "value": "R$ 40.30"}}]

Document:
{text}"""


class RemoteLLMService(BaseLLMService):
    """Calls any OpenAI-compatible remote LLM (OpenAI, Groq, Mistral, Anthropic, etc.)."""

    def __init__(self):
        """Read connection config from LLM_REMOTE_URL, LLM_REMOTE_API_KEY, LLM_REMOTE_MODEL."""
        self.url = os.environ.get("LLM_REMOTE_URL")
        self.api_key = os.environ.get("LLM_REMOTE_API_KEY")
        self.model = os.environ.get("LLM_REMOTE_MODEL")

    def extract(self, text: str) -> list[dict]:
        response = requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "x-api-key": self.api_key, # For Claude only
                "anthropic-version": "2026-06-01" # For claude only
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": PROMPT.format(text=text)}],
                "max_tokens": 1024
            }
        )
        body = response.json()

        # OpenAI-compatibility format
        if "choices" in body:
            content = body["choices"][0]["message"]["content"]
        # Claude-compatibility format
        else:
            content = body["content"][0]["text"]
        
        return json.loads(content)
