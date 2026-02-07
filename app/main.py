from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.db import create_pool
from app.embeddings import create_provider
from app.routes.docs import router as docs_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.db_pool = await create_pool()
    app.state.embedding_provider = create_provider()
    yield
    await app.state.embedding_provider.close()
    await app.state.db_pool.close()


app = FastAPI(title="cdmad-reference-vdb", lifespan=lifespan)
app.include_router(docs_router)


@app.get("/")
async def root():
    return {"service": "cdmad-reference-vdb", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok"}
