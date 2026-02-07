from __future__ import annotations

from typing import List

import httpx

from app.config import OPENAI_API_KEY, EMBEDDING_MODEL, VECTOR_DIMENSION
from app.embeddings.base import EmbeddingProvider


class OpenAIProvider(EmbeddingProvider):
    def __init__(self) -> None:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set")
        self._client = httpx.AsyncClient(
            base_url="https://api.openai.com",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            timeout=30.0,
        )

    async def embed(self, text: str) -> List[float]:
        try:
            resp = await self._client.post(
                "/v1/embeddings",
                json={"model": EMBEDDING_MODEL, "input": text},
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"OpenAI embedding request failed: {exc}") from exc

        data = resp.json()
        try:
            vector = data["data"][0]["embedding"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError("Unexpected OpenAI response format") from exc

        if len(vector) != VECTOR_DIMENSION:
            raise ValueError(
                f"Dimension mismatch: model returned {len(vector)}, "
                f"expected {VECTOR_DIMENSION}"
            )
        return vector

    async def close(self) -> None:
        await self._client.aclose()
