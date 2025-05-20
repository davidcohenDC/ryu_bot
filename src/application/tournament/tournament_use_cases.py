from typing import List

from sqlalchemy.util import await_only

from src.application.tournament.tournament_commands import DeleteTournamentCommand, SaveTournamentCommand
from src.application.unit_of_work import UnitOfWork
from src.application.base_use_case import BaseUseCase, I, O
from src.application.use_cases_wrappers import wrap_use_cases_exceptions
from src.domains.tournament.entities.tournament import Tournament
from src.domains.tournament.value_objects.ids import TournamentId


class SaveTournamentUseCase(BaseUseCase[SaveTournamentCommand, Tournament]):

    @wrap_use_cases_exceptions
    async def execute(self, cmd: SaveTournamentCommand) -> Tournament:
        tour: Tournament = cmd.to_domain()

        async with self._uow as uow:
            saved: Tournament = await uow.tournaments.save(tour)

        return saved

class DeleteTournamentUseCase(BaseUseCase[DeleteTournamentCommand, TournamentId]):

    @wrap_use_cases_exceptions
    async def execute(self, cmd: DeleteTournamentCommand) -> TournamentId:
        tour_id = TournamentId(cmd.id)

        async with self._uow as uow:
            tour_id: TournamentId = await uow.tournaments.delete(tour_id)

        return tour_id


class ListTournamentsUseCase(BaseUseCase[None, List[Tournament]]):

    @wrap_use_cases_exceptions
    async def execute(self, _input: None = None) -> List[Tournament]:

        async with self._uow as uow:
            results = await uow.tournaments.get_all()

        return results