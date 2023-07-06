from dataclasses import dataclass
from typing import Optional


@dataclass
class EndOfSeasonCommand:
    league_id: Optional[str]
