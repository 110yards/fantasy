from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class State(BaseModel):
    current_week: int
    current_season: int
    waivers_end: Optional[datetime] = None
    waivers_active: bool = False
    is_offseason: bool = False
