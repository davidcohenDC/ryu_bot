from __future__ import annotations

from typing import List

import aiosqlite

from src.domains.tournament.repositories.exceptions import TournamentInsertFailed, TournamentNotFound
from src.domains.models import Tournament
from src.domains.tournament.repositories.repository import TournamentRepository

class SQLiteTournamentRepository(TournamentRepository):
    """Implementazione asincrona su database SQLite."""

    def __init__(self, connection: aiosqlite.Connection) -> None:
        self._db = connection

    # ------------------------------------------------------------------ #
    #  MAPPING helper                                                    #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _map(row: tuple) -> Tournament:
        return Tournament(
            id=row[0],
            server_id=row[1],
            name=row[2],
            code=row[3],
            swiss=row[4],
            top_cut=row[5],
            current_round=row[6],
            is_deleted=bool(row[7]),
            created_at=row[8],
            updated_at=row[9],
        )

    # ------------------------------------------------------------------ #
    #  CRUD                                                               #
    # ------------------------------------------------------------------ #
    async def insert(self, tournament: Tournament) -> int:
        query = """
        INSERT INTO tournaments (server_id, name, code, swiss, top_cut)
        VALUES (?, ?, ?, ?, ?)
        """
        try:
            await self._db.execute(
                query,
                (
                    tournament.server_id,
                    tournament.name,
                    tournament.code,
                    tournament.swiss,
                    tournament.top_cut,
                ),
            )
            await self._db.commit()
        except Exception as exc:
            raise TournamentInsertFailed(tournament.server_id) from exc

        # recupera id appena inserito
        fetch = """
        SELECT id FROM tournaments
        WHERE server_id = ? AND name = ?
        ORDER BY created_at DESC
        LIMIT 1
        """
        async with self._db.execute(fetch, (tournament.server_id, tournament.name)) as cur:
            row = await cur.fetchone()
            if not row:
                raise TournamentInsertFailed(tournament.server_id)
            return row[0]

    async def update(self, tournament: Tournament) -> bool:
        query = """
        UPDATE tournaments
        SET name = ?, code = ?, swiss = ?, top_cut = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND server_id = ? AND is_deleted = 0
        """
        cursor = await self._db.execute(
            query,
            (
                tournament.name,
                tournament.code,
                tournament.swiss,
                tournament.top_cut,
                tournament.id,
                tournament.server_id,
            ),
        )
        await self._db.commit()
        return cursor.rowcount > 0

    async def get_by_id(self, server_id: int, tournament_id: int) -> Tournament:
        query = """
        SELECT * FROM tournaments
        WHERE id = ? AND server_id = ? AND is_deleted = 0
        """
        async with self._db.execute(query, (tournament_id, server_id)) as cur:
            row = await cur.fetchone()
            if not row:
                raise TournamentNotFound(
                    f"Tournament {tournament_id} not found in server {server_id}."
                )
            return self._map(row)

    async def get_all(
        self, server_id: int, *, include_deleted: bool = False
    ) -> List[Tournament]:
        query = """
        SELECT * FROM tournaments
        WHERE server_id = ?
        """
        if not include_deleted:
            query += " AND is_deleted = 0"
        query += " ORDER BY created_at DESC"

        async with self._db.execute(query, (server_id,)) as cur:
            rows = await cur.fetchall()
            return [self._map(r) for r in rows]

    # ------------------------------------------------------------------ #
    #  Specific helpers                                                  #
    # ------------------------------------------------------------------ #
    async def get_code(self, server_id: int, tournament_id: int) -> str:
        query = """
        SELECT code FROM tournaments
        WHERE id = ? AND server_id = ? AND is_deleted = 0
        """
        async with self._db.execute(query, (tournament_id, server_id)) as cur:
            row = await cur.fetchone()
            if not row:
                raise TournamentNotFound(
                    f"Tournament {tournament_id} not found in server {server_id}."
                )
            return row[0]

    async def soft_delete(self, server_id: int, tournament_id: int) -> None:
        query = """
        UPDATE tournaments
        SET is_deleted = 1, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND server_id = ? AND is_deleted = 0
        """
        cur = await self._db.execute(query, (tournament_id, server_id))
        await self._db.commit()
        if cur.rowcount == 0:
            raise TournamentNotFound(
                f"Tournament {tournament_id} not found for soft delete."
            )

    async def delete(self, server_id: int, tournament_id: int) -> None:
        query = """
        DELETE FROM tournaments
        WHERE id = ? AND server_id = ?
        """
        cur = await self._db.execute(query, (tournament_id, server_id))
        await self._db.commit()
        if cur.rowcount == 0:
            raise TournamentNotFound(
                f"Tournament {tournament_id} not found for hard delete."
            )
