import asyncio


from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from infrastructure.persistence.sqlmodel.sqlmodel_uow import SqlModelUnitOfWork
from src import settings
from src.application.enums import DeletePolicy
from src.application.tournament.phase_dto import PhaseDTO
from src.application.tournament.tournament_commands import SaveTournamentCommand, DeleteTournamentCommand
from src.application.tournament.tournament_use_cases import SaveTournamentUseCase, ListTournamentsUseCase, \
    DeleteTournamentUseCase
from src.domains.tournament.value_objects.enums import PhaseType, MatchMode, GameFormat
from src.domains.tournament.value_objects.ids import TournamentId

# ────────────────────────────────────────────────────────


ENGINE = create_async_engine(url=settings.SQL_DB_URI, echo=True)

AsyncSessionFactory = async_sessionmaker(
    bind=ENGINE,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_db() -> None:
    """Crea gli schemi sul database (solo al primo run)."""
    async with ENGINE.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def delete_db() -> None:
    """Elimina il database (per test e sviluppo)."""
    async with ENGINE.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await ENGINE.dispose()
    print("DB deleted.")


async def main():

    await delete_db()
    await init_db()

    uow = SqlModelUnitOfWork(AsyncSessionFactory)

    raw_json = """
    {
        "id": "T0",
        "name": "Fast Tournament",
        "entry_code": "ALOLA",
        "game_format": "standard",
        "phases": [
            {"phase_order": 1, "type": "swiss", "rounds": 2, "mode": "BO1"},
            {"phase_order": 2, "type": "single_bracket", "rounds": 5, "mode": "BO3"}
        ]
    }
    """

    cmd1 = SaveTournamentCommand.model_validate_json(raw_json)

    save_uc = SaveTournamentUseCase(uow=uow)

    saved1 = await save_uc.execute(cmd1)
    print("🎉 Saved tournament:", saved1)


    p1: PhaseDTO = PhaseDTO(
        phase_order=1,
        type=PhaseType.SWISS,
        rounds=2,
        mode=MatchMode.BEST_OF_1,
    )

    p2: PhaseDTO = PhaseDTO(
        phase_order=2,
        type=PhaseType.SINGLE_BRACKET,
        rounds=5,
        mode=MatchMode.BEST_OF_3,
    )

    cmd2 = SaveTournamentCommand(
        id="T1",
        name="Fast Tournament",
        entry_code="ALOLA",
        game_format=GameFormat.STANDARD,
        phases=[p1, p2],
    )

    save_uc = SaveTournamentUseCase(uow=uow)
    await save_uc.execute(cmd2)
    print("🎉 Saved tournament:", save_uc)


    cmd3 = ListTournamentsUseCase(uow=uow)
    tournaments = await cmd3.execute()
    print("Tournaments in DB:")
    for t in tournaments:
        print(f"ID: {t.id}, Name: {t.name}, Entry Code: {t.entry_code}")
        for phase in t.phases:
            print(f"  Phase Order: {phase.phase_order}, Type: {phase.type}, Rounds: {phase.rounds}, Mode: {phase.mode}")



    cmd4 = DeleteTournamentCommand(
        id="T0",
        policy=DeletePolicy.HARD
    )

    delete_uc = DeleteTournamentUseCase(uow=uow)

    id = await delete_uc.execute(cmd4)
    print(f"🎉 Deleted tournament with ID: {id}")
    await ENGINE.dispose()




if __name__ == "__main__":
    asyncio.run(main())
