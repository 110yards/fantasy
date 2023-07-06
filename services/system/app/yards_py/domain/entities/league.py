from __future__ import annotations

from typing import Optional

from app.yards_py.core.base_entity import BaseEntity
from app.yards_py.domain.enums.draft_state import DraftState


class League(BaseEntity):
    name: str
    draft_state: DraftState
    season: int
    league_start_week: int
    enable_discord_notifications: bool = False

    @property
    def is_active(self) -> bool:
        return self.draft_state == "completed"

    def is_active_for_season(self, season: int) -> bool:
        return self.is_active and self.season == season


class PrivateConfig(BaseEntity):
    password: Optional[str]
    id: str = "private"
    discord_webhook_url: str = None
