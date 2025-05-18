from typing import Optional, List
from src.application.dtos.tournament_dto import TournamentDTO
from src.domains.models.enums import DeleteStrategy
from src.domains.tournament.repositories.repository import TournamentRepository
from src.domains.tournament.tournament import Tournament
from src.domains.models.ids import TournamentId
from src.domains.models.application_context import ApplicationContext

class TournamentService:
    """ Application service that encapsulates tournament persistence use cases."""

    def __init__(self, repository: TournamentRepository):
        self.repository = repository

    async def create_tournament(self, dto: TournamentDTO) -> Tournament:
        """
        Create a new tournament from DTO and persist it.
        """
        tournament = dto.to_domain()
        return await self.repository.save(tournament)

    async def get_tournament(self, tournament_id: TournamentId) -> Optional[Tournament]:
        """
        Retrieve a tournament by ID.
        """
        return await self.repository.get_by_id(tournament_id)

    async def list_tournaments(
        self,
        context: ApplicationContext,
        include_deleted: bool = False
    ) -> List[Tournament]:
        """
        List all tournaments for a given context.
        """
        return await self.repository.get_all(context, include_deleted=include_deleted)

    async def update_tournament(self, dto: TournamentDTO) -> Tournament:
        """
        Update an existing tournament based on DTO input.
        """
        tournament = dto.to_domain()
        updated = await self.repository.save(tournament)

        if not updated:
            raise ValueError(f"Tournament with ID {tournament.id} not found.")

        return tournament

    async def delete_tournament(self, tournament_id: TournamentId) -> None:
        """
        Hard delete a tournament.
        """
        await self.repository.delete(tournament_id, strategy=DeleteStrategy.HARD)

    async def soft_delete_tournament(self, tournament_id: TournamentId) -> None:
        """
        Soft delete a tournament (mark as deleted).
        """
        await self.repository.delete(tournament_id, strategy=DeleteStrategy.SOFT)

    async def get_tournament_code(self, tournament_id: TournamentId) -> Optional[str]:
        """
        Return the code used to join a tournament.
        """
        return await self.repository.get_code(tournament_id)
