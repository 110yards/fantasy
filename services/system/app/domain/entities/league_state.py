from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.core.base_entity import BaseEntity


class LeagueState(BaseEntity):
    league_command_subscription: bool = False
    last_season_recalc: Optional[datetime] = None
    waivers_active: bool = False

    id: str = "state"
