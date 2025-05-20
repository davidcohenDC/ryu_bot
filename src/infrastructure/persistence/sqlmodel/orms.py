from typing import Optional, List
from sqlmodel import SQLModel, Relationship, Field
from nanoid import generate

from src.domains.tournament.entities.tournament import Tournament
from src.domains.tournament.value_objects.enums import GameFormat, PhaseType, MatchMode
from src.domains.tournament.value_objects.ids import TournamentId
from src.domains.tournament.value_objects.phase import Phase

def make_nanoid() -> str:
    # 10 alphanumeric characters
    return generate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", 10)

class ApplicationContextORM(SQLModel, table=True):
    """
    ApplicationContext model for SQLModel.
    """
    __tablename__ = "application_context"

    id: str = Field(
        default_factory=make_nanoid,
        primary_key=True,
        max_length=10
    )
    type: str = Field(nullable=False)

    tournaments: List["TournamentORM"] = Relationship(
        back_populates="context",
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class TournamentORM(SQLModel, table=True):
    """
    Tournament model for SQLModel.
    """
    __tablename__ = "tournament"

    id : str = Field(primary_key=True, default_factory=make_nanoid)
    name: str
    game_format: str = Field(nullable=False)
    entry_code: Optional[str]
    active_phase_index: int = Field(default=0)
    active_round_index: int = Field(default=0)

    context_id: Optional[int] = Field(foreign_key="application_context.id", ondelete="SET NULL")
    is_deleted: bool = Field(default=False)

    context: Optional[ApplicationContextORM] = Relationship(
        back_populates="tournaments",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    phases: list["PhaseORM"] = Relationship(
        back_populates="tournament",
        sa_relationship_kwargs={"lazy": "selectin"},
        cascade_delete=True)

    @classmethod
    def from_domain(cls, t: Tournament) -> "TournamentORM":
        """
        Create a TournamentORM instance from a domain Tournament.
        """
        orm = cls(
            id=t.id,
            name=t.name,
            game_format=t.game_format.value,
            entry_code=t.entry_code,
            active_phase_index=t.active_phase_index,
            active_round_index=t.active_round_index,
            is_deleted=False,
            phases=[PhaseORM.from_domain(t.id if t.id else None, p) for p in t.phases]
        )
        return orm

    def to_domain(self) -> Tournament:
        """
        Convert the TournamentORM instance to a domain Tournament.
        """
        return Tournament.create(
            id=TournamentId(self.id),
            name=self.name,
            game_format=GameFormat(self.game_format),
            entry_code=self.entry_code,
            phases=tuple(p.to_domain() for p in self.phases),
            active_phase_index=self.active_phase_index,
            active_round_index=self.active_round_index,
        )


class PhaseORM(SQLModel, table=True):
    __tablename__ = "phase"

    tournament_id: int = Field(foreign_key="tournament.id", primary_key=True)
    phase_order:   int = Field(primary_key=True)
    type:          str
    rounds:        int
    mode:          str

    tournament: "TournamentORM" = Relationship(
        back_populates="phases",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    @classmethod
    def from_domain(cls, tournament_id: Optional[int], p: Phase) -> "PhaseORM":
        """
        Create a PhaseORM instance from a domain Phase.
        """
        return cls(
            tournament_id=tournament_id,
            phase_order=p.phase_order,
            type=p.type.value,
            rounds=p.rounds,
            mode=p.mode.value
        )

    def to_domain(self) -> Phase:
        """
        Convert the PhaseORM instance to a domain Phase.
        """
        return Phase.create(
            phase_order=self.phase_order,
            type=PhaseType(self.type),
            rounds=self.rounds,
            mode=MatchMode(self.mode)
        )