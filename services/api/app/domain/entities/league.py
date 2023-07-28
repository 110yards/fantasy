from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from app.core.annotate_args import annotate_args
from app.core.base_entity import BaseEntity
from app.domain.entities.draft import DraftOrder
from app.domain.entities.league_position import LeaguePosition
from app.domain.entities.schedule import PlayoffType
from app.domain.enums.draft_state import DraftState
from app.domain.enums.draft_type import DraftType


@annotate_args
class League(BaseEntity):
    name: str
    commissioner_id: str
    created: datetime
    private: bool
    draft_type: DraftType
    draft_state: DraftState
    draft_order: List[DraftOrder]
    playoff_type: Optional[PlayoffType] = None
    first_playoff_week: Optional[int] = None
    positions: Dict[str, LeaguePosition] = None
    league_command_subscription: bool = False
    registration_closed: bool = False
    enable_loser_playoff: bool = False
    schedule_generated: bool = False
    issue_46_fixed: bool = True
    waivers_active: bool = False
    league_start_week: int = 1
    is_complete: bool = False
    enable_discord_notifications: bool = False
    notifications_draft: bool = False
    notifications_end_of_week: bool = False
    notifications_transactions: bool = False
    notifications_waivers: bool = False
    enable_qb_limit: bool = False
    enable_k_limit: bool = False
    enable_rb_limit: bool = False
    season: int = 2021
    has_completed_season: bool = False
    renewed: Optional[datetime] = None
    notes: Optional[str] = None
    roster_count: Optional[int] = None
    last_season_recalc: Optional[int] = None

    @property
    def is_active(self) -> bool:
        return self.draft_state == DraftState.COMPLETE

    def is_active_for_season(self, season: int) -> bool:
        return self.is_active and self.season == season


@annotate_args
class PrivateConfig(BaseEntity):
    password: Optional[str] = None
    id: str = "private"
    discord_webhook_url: str = None
