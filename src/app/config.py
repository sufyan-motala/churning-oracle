import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.LLM_BACKEND = os.getenv("LLM_BACKEND", "openai")

        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

        self.OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
        self.OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "mistral")

        self.TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

        self.CHROMA_SERVER_HOST = os.getenv("CHROMA_SERVER_HOST", "localhost")
        self.CHROMA_SERVER_HTTP_PORT = int(os.getenv("CHROMA_SERVER_HTTP_PORT", "8000"))

        self.REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
        self.REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")

        self.API_PORT = int(os.getenv("API_PORT", "3000"))

    @property
    def is_ollama(self) -> bool:
        return self.LLM_BACKEND == "ollama"

    @property
    def is_openai(self) -> bool:
        return self.LLM_BACKEND == "openai"


config = Settings()
