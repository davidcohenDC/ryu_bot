# ─── services/tournament_service.py ───
import logging
from typing import Optional, List

from data.repositories.tournament_repository import TournamentRepository
from models.tournament_model import TournamentModel, TournamentNotFound, TournamentInsertFailed


class TournamentService:
    def __init__(self, repository: TournamentRepository):
        self._repo = repository
        self._log = logging.getLogger(__name__)

    async def upsert(self, tournament: TournamentModel) -> TournamentModel:
        try:
            # Applica default se non specificato
            swiss = tournament.swiss if tournament.swiss is not None else 0
            top_cut = tournament.top_cut if tournament.top_cut is not None else 0

            if tournament.id is None:
                # Inserimento nuovo torneo
                tournament_id = await self._repo.insert(
                    server_id=tournament.server_id,
                    name=tournament.name,
                    code=tournament.code or "",
                    swiss=swiss,
                    top_cut=top_cut
                )
            else:
                # Aggiornamento esistente
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

            return TournamentModel(
                id=tournament_id,
                server_id=tournament.server_id,
                name=tournament.name,
                code=tournament.code,
                swiss=swiss,
                top_cut=top_cut,
            )

        except TournamentNotFound:
            raise  # lascia che venga gestito nel livello chiamante

        except Exception as e:
            self._log.exception(f"[TournamentService] Error upserting tournament: {tournament}")
            raise TournamentInsertFailed(tournament.server_id) from e

    async def get_code(self, server_id: int, tournament_id: int) -> Optional[str]:
        try:
            return await self._repo.get_code(server_id, tournament_id)
        except TournamentNotFound as e:
            self._log.warning(f"[TournamentService] {e}")
            return None

    async def soft_delete(self, server_id: int, tournament_id: int) -> None:
        await self._repo.soft_delete(server_id, tournament_id)

    async def delete(self, server_id: int, tournament_id: int) -> None:
        """
        Elimina un torneo specifico dal server.
        """
        await self._repo.delete(server_id, tournament_id)

    async def get_all(self, server_id: int, include_deleted: bool = False) -> list[TournamentModel]:
        return await self._repo.get_all(server_id, include_deleted=include_deleted)
