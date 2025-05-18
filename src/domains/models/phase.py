from dataclasses import dataclass

from src.domains.models.enums import PhaseType, MatchMode


@dataclass(slots=True, frozen=True)
class Phase:
    type: PhaseType
    rounds: int
    mode: MatchMode

    def __post_init__(self):
        self._validate(self)

    @staticmethod
    def _validate(phase: "Phase") -> None:
        if phase.rounds < 0:
            raise ValueError("Number of rounds must be non-negative")