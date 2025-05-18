from enum import Enum

class GameFormat(Enum):
    """Tournament format."""

    STANDARD = "standard"
    NOEX = "noex"

class PhaseType(Enum):
    """Tournament phase type."""

    SWISS = "swiss"
    SINGLE_BRACKET = "single_bracket"

class MatchMode(Enum):
    """Match mode."""

    BEST_OF_1 = "BO1"
    BEST_OF_3 = "BO3"

class ApplicationContextType(Enum):
    """Application context type."""

    DISCORD = "discord"
    TELEGRAM = "telegram"

class DeleteStrategy(Enum):
    """Delete strategy."""

    SOFT = "soft"
    HARD = "hard"

