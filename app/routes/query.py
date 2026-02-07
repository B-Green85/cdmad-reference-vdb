from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException, Request

from app.models import QueryRequest, QueryResponse, QueryResult

router = APIRouter(prefix="/v1", tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def query_docs(body: QueryRequest, request: Request) -> QueryResponse:
    # Clamp k to protect system resources
    k = max(1, min(body.k, 50))

    provider = request.app.state.embedding_provider
    pool = request.app.state.db_pool

    try:
        vector = await provider.embed(body.query)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    vector_str = "[" + ",".join(str(v) for v in vector) + "]"

    # Build query with optional filters
    conditions: List[str] = []
    params: list = [vector_str]

    if body.type is not None:
        conditions.append(f"type = %s")
        params.append(body.type)
    if body.role is not None:
        conditions.append(f"role = %s")
        params.append(body.role)
    if body.tags:
        conditions.append(f"tags @> %s")
        params.append(body.tags)

    where = ""
    if conditions:
        where = "WHERE " + " AND ".join(conditions)

    sql = f"""
        SELECT id, type, role, tags, text,
               embedding <=> %s::vector AS score
        FROM docs
        {where}
        ORDER BY score
        LIMIT %s
    """
    params.append(k)

    try:
        async with pool.connection() as conn:
            cur = await conn.execute(sql, params)
            rows = await cur.fetchall()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}") from exc

    results = [
        QueryResult(
            id=row[0],
            type=row[1],
            role=row[2],
            tags=row[3],
            text=row[4],
            score=row[5],
        )
        for row in rows
    ]
    return QueryResponse(results=results)
