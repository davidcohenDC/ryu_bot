from src.shared.repository_exceptions import (
    NotFoundError, InsertError, DeleteError, UpdateError
)

class TournamentNotFoundError(NotFoundError):
    """Exception raised when a tournament is not found."""
    def __init__(self, code: int = 2001):
        super().__init__("Tournament", code)

class TournamentSaveError(InsertError):
    """Exception raised when saving a tournament fails."""
    def __init__(self, code: int = 2002):
        super().__init__("Tournament", code)

class TournamentDeleteError(DeleteError):
    """Exception raised when deleting a tournament fails."""
    def __init__(self, code: int = 2003):
        super().__init__("Tournament", code)
