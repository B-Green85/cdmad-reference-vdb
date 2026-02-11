from __future__ import annotations

from app.embeddings.base import EmbeddingProvider
from app.embeddings.external import ExternalHTTPProvider


def create_provider() -> EmbeddingProvider:
    # Vendor-neutral: embeddings are fetched via external HTTP endpoint contract.
    return ExternalHTTPProvider()