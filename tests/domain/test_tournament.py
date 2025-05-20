import pytest

from src.domains.tournament.entities.tournament import Tournament
from src.domains.tournament.value_objects.ids import TournamentId
from src.domains.tournament.value_objects.phase import Phase
from src.domains.tournament.value_objects.enums import (
    PhaseType, MatchMode, GameFormat
)
from src.shared.utils import between

@pytest.fixture
def phases():
    return (
        Phase.create(1, PhaseType.SWISS, 2, MatchMode.BEST_OF_1),
        Phase.create(2, PhaseType.SINGLE_BRACKET, 3, MatchMode.BEST_OF_3),
    )

@pytest.fixture
def tournament_id():
    return TournamentId("T1")

@pytest.fixture
def game_format():
    return GameFormat.STANDARD

@pytest.fixture
def make_tournament(phases, tournament_id, game_format):
    """
    Fixture builder: restituisce una funzione per creare
    istanze di Tournament con parametri opzionali sovrascrivibili.
    """
    def _builder(**kwargs):
        return Tournament.create(
            id=tournament_id,
            name="Test Tournament",
            game_format=game_format,
            entry_code=None,
            phases=phases,
            **kwargs
        )
    return _builder

class TestTournament:
    def test_factory_and_properties(self, make_tournament, phases):
        t = make_tournament()
        assert t.active_phase_index == 0
        assert t.active_round_index == 0
        assert t.active_phase == phases[0]
        assert not t.is_last_phase
        assert not t.is_last_round_in_phase

    def test_advance_within_phase(self, make_tournament):
        t = make_tournament()
        t2 = t.advance()
        assert t2.active_phase_index == 0
        assert t2.active_round_index == 1

    def test_advance_to_next_phase(self, make_tournament):
        # ultima round della prima fase
        t = make_tournament(active_round_index=1)
        t2 = t.advance()
        assert t2.active_phase_index == 1
        assert t2.active_round_index == 0

    def test_advance_at_end(self, make_tournament):
        # ultima fase e ultima round
        t = make_tournament(active_phase_index=1, active_round_index=2)
        t2 = t.advance()
        assert t2 == t  # rimane invariato

    def test_reset(self, make_tournament):
        t = make_tournament(active_phase_index=1, active_round_index=1)
        t2 = t.reset()
        assert (t2.active_phase_index, t2.active_round_index) == (0, 0)

    def test_reorder_phase(self, make_tournament, phases):
        t = make_tournament()
        t2 = t.reorder_phase(0, 1)
        # dopo il reorder, phase_order è ricalcolato in base alla nuova posizione
        assert t2.phases[0].phase_order == 1
        assert t2.phases[1].phase_order == 2
        # l’istanza originale rimane immutata
        assert t.phases == phases

def test_between_utility():
    assert between(0, 0, 2)
    assert between(1, 0, 2)
    assert not between(2, 0, 2)  # upper bound esclusivo
