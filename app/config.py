from __future__ import annotations

import os


def get_postgres_dsn() -> str:
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    user = os.environ.get("POSTGRES_USER", "cdmad")
    password = os.environ.get("POSTGRES_PASSWORD", "cdmad")
    db = os.environ.get("POSTGRES_DB", "cdmad_vdb")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


EMBEDDING_PROVIDER: str = os.environ.get("EMBEDDING_PROVIDER", "ollama")
EMBEDDING_MODEL: str = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
VECTOR_DIMENSION: int = int(os.getenv("VECTOR_DIMENSION", "768"))