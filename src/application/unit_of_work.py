from abc import ABC, abstractmethod
from typing import Any

from src.domains.tournament.repository import TournamentRepository


class UnitOfWork(ABC):
    """Contract that every UoW must respect."""

    @property
    @abstractmethod
    def tournaments(self) -> TournamentRepository:
        ...

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        ...

    @abstractmethod
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        ...

    @abstractmethod
    async def commit(self) -> None:
        ...

    @abstractmethod
    async def rollback(self) -> None:
        ...