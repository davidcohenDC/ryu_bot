from dataclasses import dataclass
from datetime import datetime
from typing import Optional

"""Tournament model representing a tournament in the system."""
@dataclass(slots=True, frozen=True)
class Tournament:
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

