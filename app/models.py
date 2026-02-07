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
