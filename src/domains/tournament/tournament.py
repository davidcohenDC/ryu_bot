from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Optional, Tuple

from src.domains.models.application_context import ApplicationContext
from src.domains.models.enums import GameFormat
from src.domains.models.ids import TournamentId
from src.domains.models.phase import Phase
from src.shared.utils import between

# ------- domain model aggregate --------
@dataclass(slots=True, frozen=True)
class Tournament:
    id: Optional[TournamentId]
    name: str
    code: Optional[str]
    game_format: GameFormat
    phases: Tuple[Phase, ...]
    context: Optional[ApplicationContext] = None
    active_phase_index: int = 0 # Index (0-based) of the current phase
    active_round_index: int = 0 # Index (0-based) of the current round within the active phase

    def __post_init__(self):
        self._validate_format(self)

    # ------- factory --------
    @classmethod
    def create(
        cls,
        name: str,
        code: Optional[str],
        game_format: GameFormat,
        phases: Tuple[Phase, ...],
        context: Optional[ApplicationContext] = None,
    ) -> Tournament:
        """Factory method to safely construct a Tournament aggregate."""
        return cls(
            id=None,
            name=name,
            code=code,
            game_format=game_format,
            phases=phases,
            context=context,
            active_phase_index=0,
            active_round_index=0,
        )

    # ------- validation --------

    @staticmethod
    def _validate_format(tour: "Tournament"):
        if not all(isinstance(p, Phase) for p in tour.phases):
            raise TypeError("All items in phases must be Phase instances")

        if not tour.phases:
            raise ValueError("Tournament must have at least one phase")

        if not between(
                value=tour.active_phase_index,
                lower=0,
                upper=len(tour.phases)
        ):
            raise ValueError("Invalid active phase index")

        if not between(
                value=tour.active_round_index,
                lower=0,
                upper=tour.active_phase.rounds
        ):
            raise ValueError("Invalid active round index for current phase")

    # ------- properties --------

    @property
    def active_phase(self) -> Phase:
        return self.phases[self.active_phase_index]

    @property
    def is_last_phase(self) -> bool:
        return self.active_phase_index == len(self.phases) - 1

    @property
    def is_last_round_in_phase(self) -> bool:
        return self.active_round_index == self.active_phase.rounds - 1

    # -------- behaviour ---------

    def advance(self) -> Tournament:
        """
        Advance to the next round or phase.
        """
        if not self.is_last_round_in_phase:
            return replace(self, active_round_index=self.active_round_index + 1)

        if not self.is_last_phase:
            return replace(self,
                           active_phase_index=self.active_phase_index + 1,
                           active_round_index=0)

        return self