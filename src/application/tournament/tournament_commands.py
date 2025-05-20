from typing import List
from pydantic import BaseModel, Field

from src.application.enums import DeletePolicy
from src.application.tournament.phase_dto import PhaseDTO
from src.domains.tournament.entities.tournament import Tournament
from src.domains.tournament.value_objects.enums import GameFormat
from src.domains.tournament.value_objects.ids import TournamentId


class SaveTournamentCommand(BaseModel):
    id: str = Field(..., description="The ID of the tournament")
    name: str = Field(..., min_length=1, description="The name of the tournament")
    game_format: GameFormat = Field(
        GameFormat.STANDARD,
        description="The format of the game (e.g., STANDARD, NOEX)",
    )
    entry_code: str = Field(
        None,
        description="The entry code for the tournament (optional)",
    )
    phases: List[PhaseDTO] = Field(
        default_factory=list,
        description="A list of phases in the tournament",
    )

    def to_domain(self):

        return Tournament.create(
            id=TournamentId(self.id),
            name=self.name,
            game_format=self.game_format,
            entry_code=self.entry_code,
            phases=tuple(p.to_domain() for p in self.phases),
        )

class DeleteTournamentCommand(BaseModel):
    id: str = Field(..., description="The ID of the tournament to delete")
    policy: DeletePolicy = Field(
        DeletePolicy.HARD,
        description="The strategy to use for deletion (soft or hard)",
    )

    def to_domain(self) -> TournamentId:
        return TournamentId(self.id)
