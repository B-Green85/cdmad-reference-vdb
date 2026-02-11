from __future__ import annotations

import json
from typing import Any, List

import httpx
from jsonpath_ng import parse as jsonpath_parse

from app.config import (
    EMBEDDING_ENDPOINT_URL,
    EMBEDDING_HEADERS_JSON,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION,
    EMBEDDING_RESPONSE_PATH,
    EMBEDDING_TIMEOUT_SECONDS,
)
from app.embeddings.base import EmbeddingProvider


class ExternalHTTPProvider(EmbeddingProvider):
    def __init__(self) -> None:
        if not EMBEDDING_ENDPOINT_URL:
            raise RuntimeError("EMBEDDING_ENDPOINT_URL is required")
        if not EMBEDDING_MODEL:
            raise RuntimeError("EMBEDDING_MODEL is required")

        self._endpoint = EMBEDDING_ENDPOINT_URL  # full URL; do not construct paths
        self._model = EMBEDDING_MODEL
        self._dim = EMBEDDING_DIMENSION
        self._timeout = float(EMBEDDING_TIMEOUT_SECONDS)

        headers: dict[str, str] = {}
        if EMBEDDING_HEADERS_JSON:
            try:
                parsed = json.loads(EMBEDDING_HEADERS_JSON)
            except Exception as exc:
                raise RuntimeError("EMBEDDING_HEADERS_JSON must be valid JSON") from exc
            if not isinstance(parsed, dict):
                raise RuntimeError("EMBEDDING_HEADERS_JSON must be a JSON object")
            headers = {str(k): str(v) for k, v in parsed.items()}

        headers.setdefault("Content-Type", "application/json")
        self._headers = headers

        self._jsonpath = jsonpath_parse(EMBEDDING_RESPONSE_PATH)
        self._client = httpx.AsyncClient(timeout=self._timeout)

    async def embed(self, text: str) -> List[float]:
        payload = {"model": self._model, "input": text}

        try:
            resp = await self._client.post(
                self._endpoint,
                headers=self._headers,
                json=payload,
            )
            resp.raise_for_status()
            body: Any = resp.json()
        except Exception as exc:
            raise RuntimeError(f"Embedding request failed: {exc}") from exc

        matches = [m.value for m in self._jsonpath.find(body)]
        if not matches:
            raise RuntimeError(
                f"Embedding responsePath '{EMBEDDING_RESPONSE_PATH}' did not match response"
            )

        vec = matches[0]
        if not isinstance(vec, list):
            raise RuntimeError("Embedding extracted value is not a list")

        if len(vec) != self._dim:
            raise RuntimeError(
                f"Embedding dimension mismatch: got {len(vec)}, expected {self._dim}"
            )

        out: List[float] = []
        for x in vec:
            if not isinstance(x, (int, float)):
                raise RuntimeError("Embedding contains non-numeric values")
            out.append(float(x))

        return out

    async def aclose(self) -> None:
        await self._client.aclose()