from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True, frozen=True)
class TournamentModel:
    server_id: int
    name: str
    code: Optional[str] = None
    swiss: int = 0
    top_cut: int = 0
    current_round: int = 0
    is_deleted: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None

class RepositoryError(Exception):
    """Errore generico nel repository."""

class TournamentNotFound(RepositoryError):
    """Il torneo non esiste nel DB."""

class TournamentInsertFailed(RepositoryError):
    """Errore nel salvataggio del torneo."""