class RepositoryError(Exception):
    """Generic error in the repository."""

class TournamentNotFound(RepositoryError):
    """The tournament does not exist in the database."""

class TournamentInsertFailed(RepositoryError):
    """Error saving the tournament."""