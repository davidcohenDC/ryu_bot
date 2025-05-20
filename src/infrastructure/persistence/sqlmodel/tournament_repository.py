from typing import Optional, List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import logging
from src.domains.tournament.entities.tournament import Tournament
from src.domains.tournament.repository import TournamentRepository
from src.domains.tournament.value_objects.ids import TournamentId
from src.infrastructure.persistence.sqlmodel.orms import TournamentORM
from src.infrastructure.persistence.sqlmodel.sqlmodel_wrappers import wrap_repo_exceptions

logger = logging.getLogger("SQLModelTournamentRepository")

class SQLModelTournamentRepository(TournamentRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    @wrap_repo_exceptions
    async def save(self, tournament: Tournament) -> Tournament:
        logger.debug("Repository.save(): start, tournament=%r", tournament.id)
        t_orm = TournamentORM.from_domain(tournament)
        self.session.add(t_orm)
        logger.debug("Repository.save(): flushed add, now flushing")
        await self.session.flush()
        logger.debug("Repository.save(): flush complete")
        return t_orm.to_domain()

    @wrap_repo_exceptions
    async def get_by_id(self, tournament_id: TournamentId) -> Optional[Tournament]:
        stmt = (
            select(TournamentORM)
            .where(TournamentORM.id == tournament_id)
            .where(TournamentORM.is_deleted == False)
        )
        result = await self.session.exec(stmt)
        t_orm = result.one_or_none()
        return t_orm.to_domain() if t_orm else None

    @wrap_repo_exceptions
    async def get_all(self) -> List[Tournament]:
        stmt = select(TournamentORM)
        result = await self.session.exec(stmt)
        return [t_orm.to_domain() for t_orm in result.all()]

    @wrap_repo_exceptions
    async def delete(self, tournament_id: TournamentId) -> TournamentId:
        """
        Soft‐delete o hard‐delete. Qui chiamiamo direttamente commit().
        """
        print("SQLModelTournamentRepository.delete(): tournament_id=", tournament_id)
        stmt = select(TournamentORM).where(TournamentORM.id == tournament_id)
        result = await self.session.exec(stmt)
        tour = result.one()
        await self.session.delete(tour)
        return TournamentId(tournament_id)
