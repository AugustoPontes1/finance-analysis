

class BaseLLMService:
    def extract(self, text: str) -> dict[dict]:
        raise NotImplementedError