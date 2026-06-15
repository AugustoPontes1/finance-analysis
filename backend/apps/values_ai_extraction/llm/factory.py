import os
import logging

from backend.apps.values_ai_extraction.llm.remote import RemoteLLMService
from backend.apps.values_ai_extraction.llm.local import LocalLLMService

logger = logging.getLogger(__name__)


def get_llm_service():
    """Return LocalLLMService when LLM_PROVIDER=local, otherwise RemoteLLMService."""
    provider = os.environ.get("LLM_PROVIDER", "remote")
    logger.debug(f"LLM_PROVIDER={provider}")
    if provider == "local":
        logger.info("Using LocalLLMService")
        return LocalLLMService()
    logger.info("Using RemoteLLMService")
    return RemoteLLMService()