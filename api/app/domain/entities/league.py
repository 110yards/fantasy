from __future__ import annotations
from api.app.domain.entities.league_position import LeaguePosition
from api.app.domain.entities.draft import DraftOrder
from api.app.domain.entities.schedule import PlayoffType

from datetime import datetime
from typing import Dict, List, Optional

from api.app.core.annotate_args import annotate_args
from api.app.core.base_entity import BaseEntity
from api.app.domain.enums.draft_state import DraftState
from api.app.domain.enums.draft_type import DraftType


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


@annotate_args
class PrivateConfig(BaseEntity):
    password: Optional[str]
    id: str = "private"
    discord_webhook_url: str = None
