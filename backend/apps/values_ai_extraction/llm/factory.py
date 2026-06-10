import os

from backend.apps.values_ai_extraction.llm.remote import RemoteLLMService
from backend.apps.values_ai_extraction.llm.local import LocalLLMService

def get_llm_service():
    """Return LocalLLMService when LLM_PROVIDER=local, otherwise RemoteLLMService."""
    if os.environ.get("LLM_PROVIDER") == "local":
        return LocalLLMService()
    return RemoteLLMService()