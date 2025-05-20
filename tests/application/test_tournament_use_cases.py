import pytest
from unittest.mock import AsyncMock
from src.application.tournament.tournament_use_cases import SaveTournamentUseCase, DeleteTournamentUseCase, ListTournamentsUseCase
from src.application.tournament.tournament_commands import SaveTournamentCommand, DeleteTournamentCommand

@pytest.fixture
def fake_uow():
    repo = AsyncMock()
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.tournaments = repo
    return uow

class TestSaveTournamentUseCase:
    @pytest.mark.asyncio
    async def test_execute_saves_and_returns(self, fake_uow):
        cmd = SaveTournamentCommand(id="T1", name="X", game_format=..., entry_code="", phases=[])
        fake_uow.tournaments.save.return_value = "SAVED"
        uc = SaveTournamentUseCase(fake_uow)
        result = await uc.execute(cmd)
        fake_uow.tournaments.save.assert_awaited_once()
        assert result == "SAVED"

# Stessi pattern per Delete e List, inclusi scenari in cui repo solleva EntityNotFoundRepositoryError
