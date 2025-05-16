from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ..models.tournament import Tournament


class TournamentRepository(ABC):
    """Contratto che ogni persister di tornei deve rispettare."""

    # ---- CRUD base -------------------------------------------------------
    @abstractmethod
    async def insert(self, tournament: Tournament) -> int: ...

    @abstractmethod
    async def update(self, tournament: Tournament) -> bool: ...

    @abstractmethod
    async def get_by_id(self, server_id: int, tournament_id: int) -> Tournament: ...

    @abstractmethod
    async def get_all(
        self, server_id: int, *, include_deleted: bool = False
    ) -> List[Tournament]: ...

    # ---- specific use-cases ---------------------------------------------
    @abstractmethod
    async def get_code(self, server_id: int, tournament_id: int) -> str: ...

    @abstractmethod
    async def soft_delete(self, server_id: int, tournament_id: int) -> None: ...

    @abstractmethod
    async def delete(self, server_id: int, tournament_id: int) -> None: ...
