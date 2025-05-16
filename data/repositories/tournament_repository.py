from abc import ABC
from typing import Optional, List
from data.repositories.base import BaseRepository
from models.tournament_model import TournamentModel, TournamentNotFound, TournamentInsertFailed


class TournamentRepository(BaseRepository, ABC):

    @staticmethod
    def _map(row: tuple) -> TournamentModel:
        return TournamentModel(
            id=row[0],
            server_id=row[1],
            name=row[2],
            code=row[3],
            swiss=row[4],
            top_cut=row[5],
            current_round=row[6],
            is_deleted=bool(row[7]),
            created_at=row[8],
            updated_at=row[9]
        )

    async def insert(self, server_id: int, name: str, code: str, swiss: int = 0, top_cut: int = 0) -> int:
        query = """
            INSERT INTO tournaments (server_id, name, code, swiss, top_cut)
            VALUES (?, ?, ?, ?, ?)
        """
        try:
            await self._db.execute(query, (server_id, name, code, swiss, top_cut))
            await self._db.commit()
        except Exception as e:
            raise TournamentInsertFailed(server_id) from e

        fetch_query = """
            SELECT id FROM tournaments
            WHERE server_id = ? AND name = ?
            ORDER BY created_at DESC
            LIMIT 1
        """
        async with self._db.execute(fetch_query, (server_id, name)) as cursor:
            row = await cursor.fetchone()
            if not row:
                raise TournamentInsertFailed(server_id)
            return row[0]

    async def update(
            self,
            server_id: int,
            tournament_id: int,
            name: str,
            code: str,
            swiss: int = 0,
            top_cut: int = 0
    ) -> bool:
        query = """
            UPDATE tournaments
            SET name = ?, code = ?, swiss = ?, top_cut = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND server_id = ? AND is_deleted = 0
        """
        cursor = await self._db.execute(query, (name, code, swiss, top_cut, tournament_id, server_id))
        await self._db.commit()
        return cursor.rowcount > 0

    async def get_code(self, server_id: int, tournament_id: int) -> Optional[str]:
        query = """
            SELECT code 
            FROM tournaments
            WHERE server_id = ? AND id = ? AND is_deleted = 0
        """
        async with self._db.execute(query, (server_id, tournament_id)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                raise TournamentNotFound(f"Tournament {tournament_id} not found in server {server_id}.")
            return row[0]

    async def get_all(self, server_id: int, include_deleted: bool = False) -> List[TournamentModel]:
        query = """
            SELECT * FROM tournaments
            WHERE server_id = ?
            {}
            ORDER BY created_at DESC
        """.format("" if include_deleted else "AND is_deleted = 0")

        async with self._db.execute(query, (server_id,)) as cursor:
            rows = await cursor.fetchall()
            return [self._map(row) for row in rows]

    async def soft_delete(self, server_id: int, tournament_id: int) -> None:
        query = """
            UPDATE tournaments
            SET is_deleted = 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND server_id = ?
        """
        await self._db.execute(query, (tournament_id, server_id))
        await self._db.commit()

    async def delete(self, server_id: int, tournament_id: int) -> None:
        query = """
            DELETE FROM tournaments
            WHERE id = ? AND server_id = ?
        """
        await self._db.execute(query, (tournament_id, server_id))
        await self._db.commit()

    async def exists(self, server_id: int, tournament_id: int) -> bool:
        query = """
            SELECT 1
            FROM tournaments
            WHERE id = ? AND server_id = ? AND is_deleted = 0
        """
        async with self._db.execute(query, (tournament_id, server_id)) as cursor:
            return await cursor.fetchone() is not None
