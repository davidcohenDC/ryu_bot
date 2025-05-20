from typing import List, TYPE_CHECKING, Optional
from pydantic import Field, field_validator, ConfigDict

from src.application.base_dto import BaseDTO
from src.application.tournament.phase_dto import PhaseDTO
from src.domains.tournament.value_objects.enums import GameFormat
from src.domains.tournament.entities.tournament import Tournament
from src.domains.tournament.value_objects.ids import TournamentId

if TYPE_CHECKING:
    from src.domains.tournament.entities.tournament import Tournament

class TournamentDTO(BaseDTO[Tournament]):
    """Data Transfer Object for Tournament.

    This class is used to transfer data between different layers of the application.
    It includes validation and conversion methods to and from the domain model.
    """
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Tournament code")
    name: str = Field(..., min_length=1, description="Tournament name")
    game_format: GameFormat = Field(..., description="Game format (e.g. 'standard')")
    entry_code: Optional[str] = Field(None, description="Entry code for the tournament")
    phases: List[PhaseDTO] = Field(..., min_length=1, description="List of phases in the tournament")
    active_phase_index: int = Field(0, ge=0, description="Index of the current phase")
    active_round_index: int = Field(0, ge=0, description="Index of the current round within the active phase")

    # ---- Runtime validation (for untrusted inputs) ----
    @classmethod
    @field_validator("phases")
    def validate_phases_not_empty(cls, value: List[PhaseDTO]) -> List[PhaseDTO]:
        """Validate that the phases list is not empty."""
        if not value:
            raise ValueError("Tournament must have at least one phase.")
        return value

    def to_domain(self) -> Tournament:
        """Convert the DTO to a domain object.
        Validate the data and convert it to the domain model.

        Returns:
            Tournament: The domain model of the tournament.
        """
        return Tournament.create(
            id=TournamentId(self.id),
            name=self.name,
            game_format=self.game_format,
            entry_code=self.entry_code,
            phases=tuple(p.to_domain() for p in self.phases),
            active_phase_index=self.active_phase_index,
            active_round_index=self.active_round_index,
        )

    @classmethod
    def from_domain(cls, tournament: Tournament) -> "TournamentDTO":
        """Convert a domain object to a DTO.
        This method is used to convert a domain object to a DTO for data transfer.

        Args:
            tournament (Tournament): The domain object to convert.
        Returns:
            TournamentDTO: The converted DTO.
        """
        return cls(
            id=tournament.id,
            name=tournament.name,
            game_format=tournament.game_format,
            entry_code=tournament.entry_code,
            phases=[PhaseDTO.from_domain(p) for p in tournament.phases],
            active_phase_index=tournament.active_phase_index,
            active_round_index=tournament.active_round_index,
        )
