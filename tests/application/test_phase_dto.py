import pytest
from src.application.tournament.phase_dto import PhaseDTO
from src.domains.tournament.value_objects.enums import PhaseType, MatchMode
from src.domains.tournament.value_objects.phase import Phase

@pytest.fixture
def phase():
    return Phase.create(1, PhaseType.SWISS, 2, MatchMode.BEST_OF_1)

@pytest.fixture
def dto_data():
    return {
        "phase_order": 1,
        "type": PhaseType.SWISS,
        "rounds": 2,
        "mode": MatchMode.BEST_OF_1,
    }
class TestPhaseDTO:
    def test_phase_dto_to_from_domain(self, phase, dto_data):
        dto = PhaseDTO(**dto_data)
        domain = dto.to_domain()
        assert isinstance(domain, Phase)

        dto2 = PhaseDTO.from_domain(phase)
        assert dto2.phase_order == phase.phase_order
        assert dto2.rounds == phase.rounds

    def test_phase_dto_validation_rounds_negative(self, dto_data):
        dto_data["rounds"] = 0
        with pytest.raises(ValueError):
            PhaseDTO(**dto_data)
