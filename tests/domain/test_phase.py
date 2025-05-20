import pytest

from src.domains.tournament.value_objects.phase import Phase
from src.domains.tournament.value_objects.enums import PhaseType, MatchMode

@pytest.fixture
def default_phase_params():
    return {
        "phase_order": 1,
        "type": PhaseType.SWISS,
        "rounds": 2,
        "mode": MatchMode.BEST_OF_1,
    }

@pytest.fixture
def phase_builder(default_phase_params):
    """
    Restituisce una funzione per creare istanze di Phase
    sovrascrivendo solo i parametri che servono.
    """
    def _builder(**overrides):
        params = {**default_phase_params, **overrides}
        return Phase.create(
            phase_order=params["phase_order"],
            type=params["type"],
            rounds=params["rounds"],
            mode=params["mode"],
        )
    return _builder

class TestPhase:
    def test_creation_with_default_params(self, phase_builder):
        p = phase_builder()
        assert p.phase_order == 1
        assert p.type == PhaseType.SWISS
        assert p.rounds == 2
        assert p.mode == MatchMode.BEST_OF_1

    def test_creation_invalid_negative_rounds(self, phase_builder):
        with pytest.raises(ValueError):
            phase_builder(rounds=-1)

    def test_set_phase_order_returns_new_instance(self, phase_builder):
        p1 = phase_builder()
        p2 = p1.set_phase_order(3)
        # immutabilità e corretto aggiornamento
        assert p2.phase_order == 3
        assert p1.phase_order == 1
        assert p1 is not p2
