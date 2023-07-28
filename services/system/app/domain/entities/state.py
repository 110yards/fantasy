from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.yards_py.core.base_entity import BaseEntity


class State(BaseEntity):
    current_week: int
    current_season: int
    waivers_end: Optional[datetime] = None
    waivers_active: bool = False
    is_offseason: bool = False

    id: str = "state"

    @staticmethod
    def default(with_current_week: int = None, with_current_season: int = None, with_season_weeks: int = None, with_waivers_end: datetime = None):
        return State(
            current_week=with_current_week or 1,
            current_season=with_current_season or 2021,
            season_weeks=with_season_weeks or 16,
            waivers_end=with_waivers_end or None,
        )
