from __future__ import annotations

import os


def get_postgres_dsn() -> str:
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    user = os.environ.get("POSTGRES_USER", "cdmad")
    password = os.environ.get("POSTGRES_PASSWORD", "cdmad")
    db = os.environ.get("POSTGRES_DB", "cdmad_vdb")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


# Vendor-neutral external embeddings contract (BYO HTTPS endpoint)
EMBEDDING_ENDPOINT_URL: str = os.environ.get("EMBEDDING_ENDPOINT_URL", "")
EMBEDDING_MODEL: str = os.environ.get("EMBEDDING_MODEL", "")
EMBEDDING_DIMENSION: int = int(os.environ.get("EMBEDDING_DIMENSION", "768"))
EMBEDDING_RESPONSE_PATH: str = os.environ.get(
    "EMBEDDING_RESPONSE_PATH",
    "data[0].embedding",
)
EMBEDDING_TIMEOUT_SECONDS: int = int(os.environ.get("EMBEDDING_TIMEOUT_SECONDS", "30"))

# Optional: JSON-encoded headers dict to send with embedding requests, e.g.
# {"Authorization":"Bearer ...","X-Api-Key":"..."}
EMBEDDING_HEADERS_JSON: str = os.environ.get("EMBEDDING_HEADERS_JSON", "")