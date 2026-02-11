from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.models import UpsertRequest, UpsertResponse

from app.config import EMBEDDING_DIMENSION

router = APIRouter(prefix="/v1/docs", tags=["docs"])

UPSERT_SQL = """
INSERT INTO docs (id, type, role, tags, text, embedding)
VALUES (%s, %s, %s, %s, %s, %s::vector)
ON CONFLICT (id) DO UPDATE SET
    type = EXCLUDED.type, role = EXCLUDED.role, tags = EXCLUDED.tags,
    text = EXCLUDED.text, embedding = EXCLUDED.embedding, updated_at = NOW()
"""


@router.post("/upsert", response_model=UpsertResponse)
async def upsert_doc(body: UpsertRequest, request: Request) -> UpsertResponse:
    provider = request.app.state.embedding_provider
    pool = request.app.state.db_pool

    try:
        vector = await provider.embed(body.text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    vector_str = "[" + ",".join(str(v) for v in vector) + "]"

    try:
        async with pool.connection() as conn:
            await conn.execute(
                UPSERT_SQL,
                (body.id, body.type, body.role, body.tags, body.text, vector_str),
            )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}") from exc

    return UpsertResponse(
    id=body.id,
    status="upserted",
    embedding_dim=EMBEDDING_DIMENSION,)
