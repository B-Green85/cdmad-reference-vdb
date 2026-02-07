from __future__ import annotations

from typing import List

import httpx

from app.config import OLLAMA_BASE_URL, EMBEDDING_MODEL, VECTOR_DIMENSION
from app.embeddings.base import EmbeddingProvider


class OllamaProvider(EmbeddingProvider):
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(base_url=OLLAMA_BASE_URL, timeout=30.0)

    async def embed(self, text: str) -> List[float]:
        try:
            resp = await self._client.post(
                "/api/embeddings",
                json={"model": EMBEDDING_MODEL, "prompt": text},
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Ollama embedding request failed: {exc}") from exc

        data = resp.json()
        vector = data.get("embedding")
        if not vector:
            raise RuntimeError("Ollama returned empty embedding")

        if len(vector) != VECTOR_DIMENSION:
            raise ValueError(
                f"Dimension mismatch: model returned {len(vector)}, "
                f"expected {VECTOR_DIMENSION}"
            )
        return vector

    async def close(self) -> None:
        await self._client.aclose()
