from enum import Enum


class DeletePolicy(Enum):
    """Delete policy for tournaments."""
    SOFT = "soft"
    HARD = "hard"

