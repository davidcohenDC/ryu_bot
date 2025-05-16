# models/tournament.py  (nuovo file)
from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class Tournament:
    id: str
    name: str
    code: str