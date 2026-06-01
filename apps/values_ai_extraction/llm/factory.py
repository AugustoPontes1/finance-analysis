import os

from apps.values_ai_extraction.llm.remote import RemoteLLMService
from apps.values_ai_extraction.llm.local import LocalLLMService

def get_llm_service():
    if os.environ.get("LLM_PROVIDER") == "local":
        return LocalLLMService()
    return RemoteLLMService()