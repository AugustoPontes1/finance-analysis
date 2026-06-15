import os
import json
import logging
import re
import requests

from backend.apps.values_ai_extraction.llm.base import BaseLLMService

logger = logging.getLogger(__name__)


def _parse_llm_json(raw: str):
    """Extract a JSON array from an LLM response that may have surrounding text or code fences."""
    # 1. Direct parse
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        pass

    # 2. Extract from ```...``` or ```json...``` fences
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if fence_match:
        try:
            return json.loads(fence_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 3. Grab the first [...] block greedily
    array_match = re.search(r"\[[\s\S]*\]", raw)
    if array_match:
        try:
            return json.loads(array_match.group(0))
        except json.JSONDecodeError:
            pass

    return None

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

            result = _parse_llm_json(raw)
            if result is None:
                logger.error(f"LocalLLM returned unparseable response | raw: {raw[:400]}")
                return []

            logger.info(f"LocalLLM extraction complete: {len(result)} items")
            return result
        except Exception as e:
            logger.error(f"LocalLLMService.extract failed: {e}", exc_info=True)
            raise