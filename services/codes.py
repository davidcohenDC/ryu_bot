from cogs.code_manager import Tournament
from database import DatabaseManager


class CodeService:
    def __init__(self, repo: DatabaseManager):
        self.repo = repo

    async def upsert(self, guild: int, t: Tournament):
        await self.repo.set_code(guild, t.id, t.code, t.name)

    async def fetch(self, guild: int, tid: str) -> str | None:
        return await self.repo.get_code(guild, tid)

    async def remove(self, guild: int, tid: str):
        await self.repo.delete_code(guild, tid)

    async def list(self, guild: int) -> list[tuple[str, str]]:
        return await self.repo.list_codes(guild)
