from pydantic import Field, field_validator, ConfigDict

from src.application.base_dto import BaseDTO
from src.domains.tournament.value_objects.phase import Phase
from src.domains.tournament.value_objects.enums import PhaseType, MatchMode

class PhaseDTO(BaseDTO[Phase]):
    """
    Data Transfer Object for Phase.
    """

    model_config = ConfigDict(from_attributes=True,
                              populate_by_name=True)

    phase_order: int      = Field(..., ge=1, description="Index of the phase")
    type:        PhaseType = Field(..., description="Type of the phase")
    rounds:      int      = Field(..., ge=0, description="Number of rounds")
    mode:        MatchMode = Field(..., description="Match mode, e.g., Swiss, Round Robin")

    @field_validator("rounds")
    @classmethod
    def positive_rounds(cls, v: int) -> int:
        """
        Checks that the number of rounds is at least 1.
        """
        if v < 1:
            raise ValueError("Rounds must be at least 1")
        return v

    def to_domain(self) -> Phase:
        return Phase.create(
            phase_order=self.phase_order,
            type=self.type,
            rounds=self.rounds,
            mode=self.mode
        )

    @classmethod
    def from_domain(cls, phase: Phase) -> "PhaseDTO":
        return cls(
            phase_order=phase.phase_order,
            type=phase.type,
            rounds=phase.rounds,
            mode=phase.mode
        )
