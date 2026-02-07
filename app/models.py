from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class UpsertRequest(BaseModel):
    id: str
    type: str
    role: Optional[str] = None
    tags: List[str] = []
    text: str


class UpsertResponse(BaseModel):
    id: str
    status: str
    embedding_dim: int


class QueryRequest(BaseModel):
    query: str
    k: int = 5
    type: Optional[str] = None
    role: Optional[str] = None
    tags: Optional[List[str]] = None


class QueryResult(BaseModel):
    id: str
    type: str
    role: Optional[str]
    tags: List[str]
    text: str
    score: float


class QueryResponse(BaseModel):
    results: List[QueryResult]
