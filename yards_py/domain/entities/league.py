from __future__ import annotations
from yards_py.domain.entities.league_position import LeaguePosition
from yards_py.domain.entities.draft import DraftOrder
from yards_py.domain.entities.schedule import PlayoffType

from datetime import datetime
from typing import Dict, List, Optional

from yards_py.core.annotate_args import annotate_args
from yards_py.core.base_entity import BaseEntity
from yards_py.domain.enums.draft_state import DraftState
from yards_py.domain.enums.draft_type import DraftType


@annotate_args
class League(BaseEntity):
    name: str
    commissioner_id: str
    created: datetime
    private: bool
    draft_type: DraftType
    draft_state: DraftState
    draft_order: List[DraftOrder]
    playoff_type: Optional[PlayoffType]
    first_playoff_week: Optional[int]
    positions: Dict[str, LeaguePosition] = None
    league_command_subscription = False
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

    @property
    def is_active(self) -> bool:
        return self.draft_state == DraftState.COMPLETE

    def is_active_for_season(self, season: int) -> bool:
        return self.is_active and self.season == season


@annotate_args
class PrivateConfig(BaseEntity):
    password: Optional[str]
    id: str = "private"
    discord_webhook_url: str = None
