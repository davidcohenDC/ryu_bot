from dataclasses import dataclass

from src.domains.models.enums import ApplicationContextType
from src.domains.models.ids import ApplicationContextId


@dataclass(frozen=True)
class ApplicationContext:
    id: ApplicationContextId # unique identifier for the context
    type: ApplicationContextType # type of the context (e.g., Discord, Telegram)

    def __post_init__(self):
        self._validate(self)

    @staticmethod
    def _validate(context: "ApplicationContext") -> None:
        if not context.id:
            raise ValueError("Context ID cannot be None")

        if not context.type:
            raise ValueError("Context type cannot be None")