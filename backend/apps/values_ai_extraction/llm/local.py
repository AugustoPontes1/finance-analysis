import os
import json
import requests

from backend.apps.values_ai_extraction.llm.base import BaseLLMService

PROMPT = """"
You are a financial document analyzer.
Extract ALL label-value pairs you can find in the document below.
Labels are names of services, stores, or descriptions. Values are monetary amounts.
Return ONLY a valid JSON array, nothing else. Example:
[{{"label": "Uber", "value": "R$ 20.50"}}, {{"label": "iFood", "value": "R$ 40.30"}}]
Document:
{text}
"""

class LocalLLMService(BaseLLMService):
    """Calls a locally-running Ollama model via its generate API."""

    def __init__(self):
        """Read connection config from LLM_MODEL_URL and LLM_MODEL_NAME."""
        self.url = os.environ.get("LLM_MODEL_URL")
        self.model = os.environ.get("LLM_MODEL_NAME")

    def extract(self, text: str) -> dict[dict]:
        response = requests.post(self.url, json ={
            "model": self.model,
            "prompt": PROMPT.format(text=text),
            "stream": False
        })

        return json.loads(response.json()["response"])