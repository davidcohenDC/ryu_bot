from abc import abstractmethod, ABC
from typing import Generic, TypeVar

from src.application.unit_of_work import UnitOfWork

I = TypeVar('I')
O = TypeVar('O')

class BaseUseCase(ABC, Generic[I, O]):
    """Base class for all use cases, handling UoW and logging."""

    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    @abstractmethod
    async def execute(self, _input: I) -> O:
        """
        Sottoclassi implementano tutta la logica qui, usando self._uow.*
        """
