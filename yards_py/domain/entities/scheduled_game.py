
from __future__ import annotations

from yards_py.core.base_entity import BaseEntity
from yards_py.domain.entities.event_type import EventType
from .game_teams import GameTeams
from .team import Team


class ScheduledGame(BaseEntity):
    date_start: str
    game_number: int
    week: int
    season: int
    event_type: EventType
    teams: GameTeams

    @staticmethod
    def map(year, data: dict) -> ScheduledGame:
        return ScheduledGame(
            id=data["game_id"],
            date_start=data["date_start"],
            game_number=data["game_number"],
            week=data["week_number"],
            season=year,
            event_type=EventType.map(data["game_type"]),
            teams=GameTeams(
                away=Team.by_abbreviation(data["away"]["abbr"]),
                home=Team.by_abbreviation(data["home"]["abbr"]),
            )
        )
