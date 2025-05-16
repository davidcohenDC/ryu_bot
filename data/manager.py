import aiosqlite


class DatabaseManager:
    def __init__(self, *, connection: aiosqlite.Connection) -> None:
        self.connection = connection

    # Warn subsystem (to be modularized into its own repository in the future)
    async def add_warning(self, user_id: int, server_id: int, moderator_id: int, reason: str) -> int:
        query = "SELECT id FROM warns WHERE user_id=? AND server_id=? ORDER BY id DESC LIMIT 1"
        async with self.connection.execute(query, (user_id, server_id)) as cursor:
            result = await cursor.fetchone()
            warning_id = result[0] + 1 if result else 1

        await self.connection.execute(
            "INSERT INTO warns(id, user_id, server_id, moderator_id, reason) VALUES (?, ?, ?, ?, ?)",
            (warning_id, user_id, server_id, moderator_id, reason),
        )
        await self.connection.commit()
        return warning_id

    async def remove_warning(self, warning_id: int, user_id: int, server_id: int) -> int:
        await self.connection.execute(
            "DELETE FROM warns WHERE id=? AND user_id=? AND server_id=?",
            (warning_id, user_id, server_id),
        )
        await self.connection.commit()

        query = "SELECT COUNT(*) FROM warns WHERE user_id=? AND server_id=?"
        async with self.connection.execute(query, (user_id, server_id)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def fetch_warnings(self, user_id: int, server_id: int) -> list:
        query = """
            SELECT user_id, server_id, moderator_id, reason, strftime('%s', created_at), id
            FROM warns
            WHERE user_id=? AND server_id=?
        """
        async with self.connection.execute(query, (user_id, server_id)) as cursor:
            return await cursor.fetchall()