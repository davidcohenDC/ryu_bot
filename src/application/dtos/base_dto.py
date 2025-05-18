from pydantic import BaseModel, Field
from typing import TypeVar, Type

TDomain = TypeVar("TDomain")

class BaseDTO(BaseModel):
    """Base class for all DTOs with conversion helpers."""

    def to_domain(self) -> TDomain:
        raise NotImplementedError("Implement in subclass")

    @classmethod
    def from_domain(cls: Type["BaseDTO"], domain: TDomain) -> "BaseDTO":
        raise NotImplementedError("Implement in subclass")

    class Config:
        use_enum_values = True  # make Enums serialize as their .value (e.g. 'swiss' instead of PhaseType.SWISS)
        orm_mode = True         # allow ORM-style objects to work with Pydantic (e.g. SQLAlchemy, domain classes)
