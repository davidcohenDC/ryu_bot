from typing import Optional

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from src.application.unit_of_work import UnitOfWork
from src.infrastructure.persistence.sqlmodel.tournament_repository import SQLModelTournamentRepository


class SqlModelUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory
        self._session: Optional[AsyncSession] = None

        self._tournaments: Optional[SQLModelTournamentRepository] = None
        # ... other repositories can be added here

    async def __aenter__(self) -> "SqlModelUnitOfWork":
        self._session = self._session_factory()
        # inject session into repositories

        self._tournaments = SQLModelTournamentRepository(self._session)
        # ... other repositories can be initialized here

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type is None:
                await self.commit()
            else:
                await self.rollback()
        finally:
            await self._session.close()

    @property
    def tournaments(self) -> SQLModelTournamentRepository:
        assert self._tournaments is not None, "Enter context before using"
        return self._tournaments

    # @property
    # def users(self) -> SQLModelUserRepository:
    #     assert self._users is not None, "Enter context before using"
    #     return self._users

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()