from __future__ import annotations

from typing import Optional

from yards_py.core.base_entity import BaseEntity
from yards_py.domain.entities.event_status import EventStatus
from yards_py.domain.entities.event_type import EventType
from yards_py.domain.entities.game_score import GameScore
from yards_py.domain.entities.game_teams import GameTeams

from .team import Team


class ScheduledGame(BaseEntity):
    date_start: str
    week_number: int
    season: int
    game_type: EventType
    away: Team
    home: Team

    @staticmethod
    def from_core(year: int, data: dict):
        game_id = data.get("game_id")

        return ScheduledGame(id=game_id, season=year, **data)
