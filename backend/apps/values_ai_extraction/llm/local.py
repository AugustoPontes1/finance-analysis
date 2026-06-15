import os
import json
import logging
import requests

from backend.apps.values_ai_extraction.llm.base import BaseLLMService

logger = logging.getLogger(__name__)

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
        logger.debug(f"LocalLLMService.extract: model={self.model}, url={self.url}, text_len={len(text)}")
        try:
            response = requests.post(self.url, json={
                "model": self.model,
                "prompt": PROMPT.format(text=text),
                "stream": False
            })
            response.raise_for_status()
            raw = response.json().get("response", "")
            logger.debug(f"LocalLLM raw response ({len(raw)} chars): {raw[:500]}")

            if not raw.strip():
                logger.warning("LocalLLM returned empty response")
                return []

            # Strip markdown code fences if present (```json ... ```)
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
                cleaned = cleaned.strip()

            result = json.loads(cleaned)
            logger.info(f"LocalLLM extraction complete: {len(result)} items")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"LocalLLM returned invalid JSON: {e} | raw: {raw[:300]}")
            return []
        except Exception as e:
            logger.error(f"LocalLLMService.extract failed: {e}", exc_info=True)
            raise