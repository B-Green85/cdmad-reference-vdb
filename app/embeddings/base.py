from __future__ import annotations

import abc
from typing import List


class EmbeddingProvider(abc.ABC):
    @abc.abstractmethod
    async def embed(self, text: str) -> List[float]:
        ...

    async def close(self) -> None:
        pass
