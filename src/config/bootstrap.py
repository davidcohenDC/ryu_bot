from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlmodel import SQLModel

from src import settings
from src.infrastructure.persistence.sqlmodel.sqlmodel_uow import SqlModelUnitOfWork

engine: AsyncEngine = create_async_engine(
    settings.SQL_DB_URI,
    echo=settings.SQL_ECHO,
    # pool_pre_ping=True,        # keep connections alive
    # pool_size=10,              # max DB connections
    # max_overflow=20,           # additional connections
)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,    # avoids detached instances issues
)

# ─────────────────────────────────────────────────────────────────────────────
# 3) Database lifecycle helpers
# ─────────────────────────────────────────────────────────────────────────────
async def init_db() -> None:
    """Create all tables (SQLModel metadata) in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def drop_db() -> None:
    """Drop all tables, for tests or local reset."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()

# ─────────────────────────────────────────────────────────────────────────────
# 4) Unit of Work factory
# ─────────────────────────────────────────────────────────────────────────────
def get_uow() -> SqlModelUnitOfWork:
    """
    Composition root for your SQLModelUnitOfWork.
    You can swap this factory for tests or for a NoSQL implementation.
    """
    return SqlModelUnitOfWork(AsyncSessionFactory)


