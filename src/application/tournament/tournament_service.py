from __future__ import annotations

import logging
from dataclasses import replace
from typing import List

from src.domains.tournament.exceptions import TournamentNotFound, TournamentInsertFailed
from src.domains.tournament.models.tournament import Tournament
from src.domains.tournament.repositories.tournament_repo import TournamentRepository

class TournamentService:
    """Application-service che gestisce i tornei."""

    def __init__(self, repo: TournamentRepository) -> None:
        self._repo = repo
        self._log = logging.getLogger(__name__)

    # ------------------------------------------------------------------ #
    #  UPSERT                                                            #
    # ------------------------------------------------------------------ #
    async def upsert(self, t: Tournament) -> Tournament:
        """Crea o aggiorna un torneo e restituisce l’istanza definitiva."""

        try:
            # ---------- INSERT ----------
            if t.id is None:
                new_id = await self._repo.insert(t)
                return replace(t, id=new_id)

            # ---------- UPDATE ----------
            # 1) recupera lo stato corrente
            current = await self._repo.get_by_id(t.server_id, t.id)

            # 2) “merge” dei campi (solo quelli non None vengono aggiornati)
            merged = replace(
                current,
                name=t.name or current.name,
                code=t.code if t.code is not None else current.code,
                swiss=t.swiss if t.swiss is not None else current.swiss,
                top_cut=t.top_cut if t.top_cut is not None else current.top_cut,
            )

            # se nulla è cambiato, restituisci direttamente
            if merged == current:
                return merged

            updated = await self._repo.update(merged)
            if not updated:
                raise TournamentNotFound(
                    f"Tournament {t.id} not found in server {t.server_id}"
                )
            return merged

        except TournamentNotFound:
            raise  # lascio gestire a chi chiama

        except Exception as exc:
            self._log.exception("Error upserting tournament: %s", t)
            raise TournamentInsertFailed(t.server_id) from exc

    # ------------------------------------------------------------------ #
    #  READ                                                              #
    # ------------------------------------------------------------------ #
    async def get_by_id(self, server_id: int, tournament_id: int) -> Tournament:
        return await self._repo.get_by_id(server_id, tournament_id)

    async def get_all(
        self, server_id: int, *, include_deleted: bool = False
    ) -> List[Tournament]:
        return await self._repo.get_all(server_id, include_deleted=include_deleted)

    async def get_code(self, server_id: int, tournament_id: int) -> str:
        return await self._repo.get_code(server_id, tournament_id)

    # ------------------------------------------------------------------ #
    #  DELETE / SOFT DELETE                                              #
    # ------------------------------------------------------------------ #
    async def soft_delete(self, server_id: int, tournament_id: int) -> None:
        await self._repo.soft_delete(server_id, tournament_id)

    async def delete(self, server_id: int, tournament_id: int) -> None:
        await self._repo.delete(server_id, tournament_id)
