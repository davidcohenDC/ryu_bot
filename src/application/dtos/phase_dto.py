from pydantic import Field

from src.application.dtos.base_dto import BaseDTO
from src.domains.models.phase import Phase, PhaseType, MatchMode

class PhaseDTO(BaseDTO):
    type: PhaseType = Field(..., description="Type of phase (e.g. 'swiss')")
    rounds: int = Field(..., ge=0, description="Number of rounds")
    mode: MatchMode = Field(..., description="Match mode (e.g. 'BO1')")

    def to_domain(self) -> Phase:
        return Phase(
            type=self.type,
            rounds=self.rounds,
            mode=self.mode
        )

    @classmethod
    def from_domain(cls, phase: Phase) -> "PhaseDTO":
        return cls(
            type=phase.type,
            rounds=phase.rounds,
            mode=phase.mode
        )
