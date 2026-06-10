

class BaseLLMService:
    """Abstract interface for LLM-based financial document extraction."""

    def extract(self, text: str) -> dict[dict]:
        """Extract label-value pairs from the given document text."""
        raise NotImplementedError