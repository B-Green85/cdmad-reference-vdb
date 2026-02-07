from __future__ import annotations

from psycopg_pool import AsyncConnectionPool

from app.config import get_postgres_dsn


async def create_pool() -> AsyncConnectionPool:
    pool = AsyncConnectionPool(conninfo=get_postgres_dsn(), open=False)
    await pool.open()
    return pool
