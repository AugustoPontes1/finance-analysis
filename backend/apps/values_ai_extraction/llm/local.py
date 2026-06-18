import os
import json
import logging
import re
import requests

from backend.apps.values_ai_extraction.llm.base import BaseLLMService

logger = logging.getLogger(__name__)


PROMPT = """"
You are a financial document analyzer.
Analyze the document below and provide a clear, natural language summary
of all financial items, amounts, and insights you find.
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

            logger.info(f"LocalLLM extraction complete: {len(raw)} chars")
            return raw
        except Exception as e:
            logger.error(f"LocalLLMService.extract failed: {e}", exc_info=True)
            raise