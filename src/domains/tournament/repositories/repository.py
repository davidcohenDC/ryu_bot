from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional

from src.domains.models.application_context import ApplicationContext
from src.domains.models.enums import DeleteStrategy
from src.domains.tournament.tournament import Tournament
from src.domains.models.ids import TournamentId

class TournamentRepository(ABC):
    """Interface that any tournament persistence mechanism must adhere to."""

    # ---- Basic CRUD operations -------------------------------------------
    @abstractmethod
    async def save(self, tournament: Tournament) -> Tournament:
        """
        Saves a tournament to the repository.

        Args:
            tournament (Tournament): The tournament instance to insert.

        Returns:
            Tournament: The saved tournament instance.

        Raises:
            RepositoryError: If the insertion fails due to a repository error.
            TournamentSaveError: If the tournament cannot be saved.
        """
        ...

    @abstractmethod
    async def get_by_id(self, tournament_id: TournamentId) -> Optional[Tournament]:
        """
        Retrieves a tournament by its ID.

        Args:
            tournament_id (TournamentId): The ID of the tournament to retrieve.

        Returns:
            Optional[Tournament]: The tournament instance if found, otherwise None.

        Raises:
            RepositoryError: If the retrieval fails due to a repository error.
            TournamentNotFoundError: If the tournament is not found in the repository.
        """
        ...

    @abstractmethod
    async def get_all(self, context: ApplicationContext, *, include_deleted: bool = False) -> List[Tournament]:
        """
        Retrieves all tournaments, with an option to include those marked as deleted.

        Args:
            context (ApplicationContext): The application context.
            include_deleted (bool, optional): If True, includes tournaments marked as deleted. Defaults to False.

        Returns:
            List[Tournament]: A list of tournaments.

        Raises:
            RepositoryError: If the retrieval fails due to a repository error.
        """
        ...

    # ---- Specific use-cases ---------------------------------------------
    @abstractmethod
    async def get_code(self, tournament_id: TournamentId) -> Optional[str]:
        """
        Retrieves the code associated with a tournament.

        Args:
            tournament_id (TournamentId): The ID of the tournament.

        Returns:
            Optional[str]: The tournament code if available, otherwise None.

        Raises:
            RepositoryError: If the retrieval fails due to a repository error.
            TournamentNotFoundError: If the tournament is not found in the repository.
        """
        ...

    @abstractmethod
    async def delete(self, tournament_id: TournamentId, strategy: DeleteStrategy) -> None:
        """
        Permanently removes a tournament from the repository.

        Args:
            tournament_id (TournamentId): The ID of the tournament to delete.
            strategy (DeleteStrategy): The strategy to use for deletion.

        Raises:
            RepositoryError: If the deletion fails due to a repository error.
            TournamentDeleteFailedError: If the deletion fails due to a repository error.
        """
        ...
