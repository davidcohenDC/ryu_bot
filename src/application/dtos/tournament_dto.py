from typing import List, Optional, Annotated
from pydantic import Field, field_validator

from src.application.dtos.base_dto import BaseDTO
from src.application.dtos.phase_dto import PhaseDTO
from src.domains.models.enums import GameFormat
from src.domains.models.application_context import ApplicationContext
from src.domains.models.ids import TournamentId
from src.domains.tournament.tournament import Tournament


class TournamentDTO(BaseDTO[Tournament]):
    id: Optional[TournamentId] = Field(None, description="Tournament ID")
    name: str = Field(..., min_length=1, description="Tournament name")
    code: Optional[str] = Field(None, description="Tournament code")
    game_format: GameFormat = Field(..., description="Game format (e.g. 'standard')")
    phases: Annotated[
        List[PhaseDTO],
        Field(..., description="Phases of the tournament", json_schema_extra={"minItems": 1})
    ]
    context: Optional[ApplicationContext] = Field(None, description="Execution context")
    active_phase_index: int = Field(0, ge=0, description="Index of the current phase")
    active_round_index: int = Field(0, ge=0, description="Index of the current round within the active phase")

    # ---- Runtime validation (for untrusted inputs) ----
    @classmethod
    @field_validator("field_name")
    def validate_phases_not_empty(cls, value: List[PhaseDTO]) -> List[PhaseDTO]:
        if not value:
            raise ValueError("Tournament must have at least one phase.")
        return value

    def to_domain(self) -> Tournament:
        return Tournament(
            id=self.id,
            name=self.name,
            code=self.code,
            game_format=self.game_format,
            phases=tuple(p.to_domain() for p in self.phases),
            context=self.context,
            active_phase_index=self.active_phase_index,
            active_round_index=self.active_round_index,
        )

    @classmethod
    def from_domain(cls, tournament: Tournament) -> "TournamentDTO":
        return cls(
            id=tournament.id,
            name=tournament.name,
            code=tournament.code,
            game_format=tournament.game_format,
            phases=[PhaseDTO.from_domain(p) for p in tournament.phases],
            context=tournament.context,
            active_phase_index=tournament.active_phase_index,
            active_round_index=tournament.active_round_index,
        )
