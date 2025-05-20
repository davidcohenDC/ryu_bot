from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, T

from src.domains.tournament.entities.tournament import Tournament
from src.domains.tournament.value_objects.ids import TournamentId


class BaseRepository(ABC):
    """Base class for repositories."""

    @abstractmethod
    async def save(self, entity) -> None:
        ...

    @abstractmethod
    async def get_by_id(self, entity_id) -> Optional[T]:
        ...
    @abstractmethod
    async def get_all(self) -> List[T]:
        ...

    @abstractmethod
    async def delete(self, entity_id) -> T:
        ...


class TournamentRepository(BaseRepository):
    """Interface that any tournament persistence mechanism must adhere to."""

    @abstractmethod
    async def save(self, tournament: Tournament) -> Tournament:
        """
        Saves a tournament to the repository.

        Args:
            tournament (Tournament): The tournament instance to insert.

        Returns:
            Tournament: The saved tournament instance.

        """
        ...

    @abstractmethod
    async def get_by_id(self, tournament_id: TournamentId) -> Optional[Tournament]:
        """
        Retrieves a tournament by its ID.

        Args:
            tournament_id (TournamentCode): The ID of the tournament to retrieve.

        Returns:
            Optional[Tournament]: The tournament instance if found, otherwise None.

        """
        ...

    @abstractmethod
    async def get_all(self) -> List[Tournament]:
        """
        Retrieves all tournaments, with an option to include those marked as deleted.

        Returns:
            List[Tournament]: A list of tournaments.

        """
        ...

    @abstractmethod
    async def delete(self, tournament_id: TournamentId) -> TournamentId:
        """
        Permanently removes a tournament from the repository.

        Args:
            tournament_id (TournamentId): The ID of the tournament to delete.

        Returns:
            The deleted tournament ID.
        """
        ...

