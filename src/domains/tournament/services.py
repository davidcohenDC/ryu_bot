import logging
from src.domains.tournament.exceptions import TournamentNotFound, TournamentInsertFailed
from src.domains.tournament.models import Tournament
from src.domains.tournament.repositories import TournamentRepository


class TournamentService:
    def __init__(self, repository: TournamentRepository):
        self._repo = repository
        self._log = logging.getLogger(__name__)

    async def upsert(self, tournament: Tournament) -> Tournament:
        try:
            # Apply default values if not provided
            swiss = tournament.swiss if tournament.swiss is not None else 0
            top_cut = tournament.top_cut if tournament.top_cut is not None else 0

            if tournament.id is None:
                # Insert new tournament
                tournament_id = await self._repo.insert(
                    server_id=tournament.server_id,
                    name=tournament.name,
                    code=tournament.code or "",
                    swiss=swiss,
                    top_cut=top_cut
                )
            else:
                # Update existing tournament
                updated = await self._repo.update(
                    server_id=tournament.server_id,
                    tournament_id=tournament.id,
                    name=tournament.name,
                    code=tournament.code or "",
                    swiss=swiss,
                    top_cut=top_cut
                )
                if not updated:
                    raise TournamentNotFound(
                        f"Tournament ID {tournament.id} not found in server {tournament.server_id}")
                tournament_id = tournament.id

            return Tournament(
                id=tournament_id,
                server_id=tournament.server_id,
                name=tournament.name,
                code=tournament.code,
                swiss=swiss,
                top_cut=top_cut,
            )

        except (TournamentNotFound, ValueError):
            raise # mananaged by the caller

        except Exception as e:
            self._log.exception(f"Error upserting tournament: {tournament}")
            raise TournamentInsertFailed(tournament.server_id) from e

    async def soft_delete(self, server_id: int, tournament_id: int) -> None:
        try:
            deleted = await self._repo.soft_delete(server_id, tournament_id)
            if not deleted:
                raise TournamentNotFound(f"Tournament ID {tournament_id} not found in server {server_id}")
        except Exception as e:
            self._log.exception(f"Error during soft delete of tournament {tournament_id} in server {server_id}")
            raise

    async def get_by_id(self, server_id: int, tournament_id: int) -> Tournament:
        try:
            tournament = await self._repo.get_by_id(server_id, tournament_id)
            if not tournament:
                raise TournamentNotFound(f"Tournament ID {tournament_id} not found in server {server_id}")
            return tournament
        except Exception as e:
            self._log.exception(f"Error retrieving tournament {tournament_id} in server {server_id}")
            raise

    async def delete(self, server_id: int, tournament_id: int) -> None:
        try:
            deleted = await self._repo.delete(server_id, tournament_id)
            if not deleted:
                raise TournamentNotFound(f"Tournament ID {tournament_id} not found in server {server_id}")
        except Exception as e:
            self._log.exception(f"Error during hard delete of tournament {tournament_id} in server {server_id}")
            raise

    async def get_all(self, server_id: int, include_deleted: bool = False) -> list[Tournament]:
        try:
            return await self._repo.get_all(server_id, include_deleted=include_deleted)
        except Exception as e:
            self._log.exception(f"Error retrieving tournaments for server {server_id}")
            return []
