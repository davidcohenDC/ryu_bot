from abc import abstractmethod
from typing import Generic, TypeVar, Type
from pydantic import BaseModel, ConfigDict

TDomain = TypeVar("TDomain")

class BaseDTO(BaseModel, Generic[TDomain]):
    """
    Base class for all DTOs, parametrizzata su TDomain.
    Usa from_attributes per sostituire il vecchio orm_mode.
    """
    model_config = ConfigDict(from_attributes=True)

    @abstractmethod
    def to_domain(self) -> TDomain:
        """
        Convert this DTO into its domain object.
        """

    @abstractmethod
    def from_domain(
        self: Type["BaseDTO[TDomain]"],
        domain: TDomain
    ) -> "BaseDTO[TDomain]":
        """
        Convert a domain object into this DTO.
        """
