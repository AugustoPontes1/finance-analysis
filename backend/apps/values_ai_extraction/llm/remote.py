import os
import logging
import requests
import json

from backend.apps.values_ai_extraction.llm.base import BaseLLMService

logger = logging.getLogger(__name__)

PROMPT = """You are a financial document analyzer.
Analyze the document below and return ONLY a valid JSON object with two fields:
- "summary": a natural language description of all financial items and insights found
- "items": a JSON array of label-value pairs where labels are names/descriptions and values are monetary amounts

Example:
{{"summary": "This document shows a transfer of R$ 1,758.91 from Visian Systems...", "items": [{{"label": "Transfer Value", "valu": "Initial Amount", "value": "R$1,774.92"}}]}}

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
        logger.debug(f"RemoteLLMService.extract: model={self.model}, url={self.url}, text_len={len(text)}")
        try:
            response = requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2026-06-01"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": PROMPT.format(text=text)}],
                    "max_tokens": 1024
                }
            )
            response.raise_for_status()
            body = response.json()
            logger.debug(f"RemoteLLM response keys: {list(body.keys())}")

            if "choices" in body:
                content = body["choices"][0]["message"]["content"]
            else:
                content = body["content"][0]["text"]

            logger.debug(f"RemoteLLM raw content ({len(content)} chars): {content[:500]}")

            if not content.strip():
                logger.warning("RemoteLLM returned empty content")
                return []

            result = json(content)
            if result is None:
                logger.error(f"RemoteLLM returned unparseable response | raw: {content[:400]}")
                return []

            logger.info(f"RemoteLLM extraction complete: {len(result)} items")
            return result
        except Exception as e:
            logger.error(f"RemoteLLMService.extract failed: {e}", exc_info=True)
            raise
