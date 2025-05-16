from __future__ import annotations
from dataclasses import dataclass, replace, field
from datetime import datetime, timezone
from typing import Optional

@dataclass(slots=True, frozen=True)
class Tournament:
    server_id: int
    name: str
    code: Optional[str] = None
    swiss: int = 0
    top_cut: int = 0
    current_round: int = 0
    is_deleted: bool = False
    created_at: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    updated_at: Optional[datetime] = None
    id: Optional[int] = None