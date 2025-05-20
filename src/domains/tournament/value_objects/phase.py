from dataclasses import dataclass, replace

from src.domains.tournament.value_objects.enums import PhaseType, MatchMode


@dataclass(slots=True, frozen=True)
class Phase:
    phase_order: int
    type: PhaseType
    rounds: int
    mode: MatchMode

    def __post_init__(self):
        self._validate(self)

    @classmethod
    def create(
        cls,
        phase_order: int,
        type: PhaseType,
        rounds: int,
        mode: MatchMode
    ) -> "Phase":
        return cls(
            phase_order=phase_order,
            type=type,
            rounds=rounds,
            mode=mode
        )


    @staticmethod
    def _validate(phase: "Phase") -> None:
        if phase.rounds < 0:
            raise ValueError("Number of rounds must be non-negative")

    def set_phase_order(self, phase_order: int) -> "Phase":
        """Restituisce una nuova Phase identica, ma con phase_number aggiornato."""
        return replace(
            self,
            phase_order=phase_order
        )