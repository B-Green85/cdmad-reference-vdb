-- 001_init.sql: pgvector extension + docs table

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS docs (
    id          TEXT PRIMARY KEY,
    type        TEXT NOT NULL,
    role        TEXT,
    tags        TEXT[] NOT NULL DEFAULT '{}',
    text        TEXT NOT NULL,
    embedding   VECTOR(1536) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_docs_type ON docs (type);
CREATE INDEX IF NOT EXISTS idx_docs_tags ON docs USING GIN (tags);
