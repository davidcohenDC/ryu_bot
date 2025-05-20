from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Tuple, List, Optional

from src.domains.tournament.value_objects.enums import GameFormat
from src.domains.tournament.value_objects.ids import TournamentId
from src.domains.tournament.value_objects.phase import Phase
from src.shared.utils import between

@dataclass(slots=True, frozen=True)
class Tournament:
    """
    Tournament entity representing a competitive event with multiple phases and rounds.
    """
    id: TournamentId
    name: str
    game_format: GameFormat
    entry_code: Optional[str]
    phases: Tuple[Phase, ...]
    active_phase_index: int = 0
    active_round_index: int = 0

    def __post_init__(self):
        self._validate_format(self)

    # ------- factory --------
    @classmethod
    def create(
        cls,
        id: TournamentId,
        name: str,
        game_format: GameFormat,
        entry_code: Optional[str],
        phases: Tuple[Phase, ...],
        active_phase_index: int = 0,
        active_round_index: int = 0,
    ) -> Tournament:
        return cls(
            id=id,
            name=name,
            game_format=game_format,
            entry_code=entry_code,
            phases=phases,
            active_phase_index=active_phase_index,
            active_round_index=active_round_index,
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

    def reset(self) -> Tournament:
        """
        Reset the tournament to the first phase and round.
        """
        return replace(self, active_phase_index=0, active_round_index=0)

    def reorder_phase(self, from_idx: int, to_idx: int) -> Tournament:
        """
        Reorder phases in the tournament.
        Raises IndexError if indices are out of range.
        """
        if not between(
                value=from_idx,
                lower=0,
                upper=len(self.phases)
        ) or not between(
                value=to_idx,
                lower=0,
                upper=len(self.phases)
        ):
            raise IndexError("Phase index out of range")


        # Create a new list of phases to avoid mutating the original tuple
        phases_list: List[Phase] = list(self.phases)
        phase: Phase = phases_list.pop(from_idx)
        phases_list.insert(to_idx, phase)

        # 2) Calculate the new phase numbers
        new_phases = tuple(
            p.set_phase_order(idx + 1)
            for idx, p in enumerate(phases_list)
        )

        # 3) Return a new Tournament instance with the updated phases
        return replace(self, phases=new_phases)