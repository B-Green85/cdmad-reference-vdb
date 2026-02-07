from __future__ import annotations

from app.config import EMBEDDING_PROVIDER
from app.embeddings.base import EmbeddingProvider


def create_provider() -> EmbeddingProvider:
    provider = EMBEDDING_PROVIDER.lower()
    if provider == "ollama":
        from app.embeddings.ollama import OllamaProvider

        return OllamaProvider()
    elif provider == "openai":
        from app.embeddings.openai import OpenAIProvider

        return OpenAIProvider()
    else:
        raise RuntimeError(
            f"Unknown EMBEDDING_PROVIDER: {EMBEDDING_PROVIDER!r}. "
            f"Supported: ollama, openai"
        )
