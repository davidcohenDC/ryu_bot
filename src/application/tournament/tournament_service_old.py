from __future__ import annotations

import logging
from dataclasses import replace
from typing import List

from src.domains.tournament.repositories.exceptions import (
    TournamentNotFound,
    TournamentInsertFailed,
)
from src.domains.models import Tournament
from src.domains.tournament.repositories.repository import TournamentRepository


class TournamentService:
    """Application service that encapsulates tournament persistence logic.

    Parameters
    ----------
    repo : TournamentRepository
        Concrete repository implementation (injected for testability).
    """

    def __init__(self, repo: TournamentRepository) -> None:
        self._repo = repo
        self._log = logging.getLogger(__name__)

    async def upsert(self, t: Tournament) -> Tournament:
        """Insert a new tournament or update an existing one.

        Strategy
        --------
        * **Insert** – if `t.id` is None, call `insert` on the repo and return
          `t` with the new ID.
        * **Update** – fetch current state, merge only non-None fields, skip
          persistence when nothing changed.

        Raises
        ------
        TournamentNotFound
            The tournament ID was not found during an update.
        TournamentInsertFailed
            Unexpected repository error.
        """
        try:
            # ---------- INSERT ----------
            if t.id is None:
                new_id = await self._repo.insert(t)
                return replace(t, id=new_id)

            # ---------- UPDATE ----------
            current = await self._repo.get_by_id(t.server_id, t.id)

            # Field-wise merge: only non-None values override current ones
            merged = replace(
                current,
                name=t.name or current.name,
                code=t.code if t.code is not None else current.code,
                swiss=t.swiss if t.swiss is not None else current.swiss,
                top_cut=t.top_cut if t.top_cut is not None else current.top_cut,
            )

            # Nothing changed → avoid unnecessary write
            if merged == current:
                return merged

            updated = await self._repo.update(merged)
            if not updated:
                raise TournamentNotFound(
                    f"Tournament {t.id} not found in server {t.server_id}"
                )
            return merged

        except TournamentNotFound:
            raise  # propagate to caller

        except Exception as exc:
            self._log.exception("Error upserting tournament: %s", t)
            raise TournamentInsertFailed(t.server_id) from exc

    # ---------- Read operations ----------
    async def get_by_id(self, server_id: int, tournament_id: int) -> Tournament:
        """Return a specific tournament or raise TournamentNotFound."""
        return await self._repo.get_by_id(server_id, tournament_id)

    async def get_all(
        self, server_id: int, *, include_deleted: bool = False
    ) -> List[Tournament]:
        """List all tournaments for a server.
        Set `include_deleted=True` to include soft-deleted ones."""
        return await self._repo.get_all(server_id, include_deleted=include_deleted)

    async def get_code(self, server_id: int, tournament_id: int) -> str:
        """Return the access code for a tournament."""
        return await self._repo.get_code(server_id, tournament_id)

    # ---------- Delete operations ----------
    async def soft_delete(self, server_id: int, tournament_id: int) -> None:
        """Mark a tournament as deleted without removing it from storage."""
        await self._repo.soft_delete(server_id, tournament_id)

    async def delete(self, server_id: int, tournament_id: int) -> None:
        """Hard-delete a tournament."""
        await self._repo.delete(server_id, tournament_id)
