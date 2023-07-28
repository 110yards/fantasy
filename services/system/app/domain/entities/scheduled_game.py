
from __future__ import annotations

from typing import Optional
from app.yards_py.core.base_entity import BaseEntity
from app.yards_py.domain.entities.event_status import EventStatus
from app.yards_py.domain.entities.event_type import EventType
from app.yards_py.domain.entities.game_score import GameScore
from app.yards_py.domain.entities.game_teams import GameTeams


class ScheduledGame(BaseEntity):
    date_start: str
    # game_number: int
    week: int
    season: int
    game_duration: Optional[int]
    event_type: EventType
    event_status: EventStatus
    score: GameScore
    teams: GameTeams

    @staticmethod
    def from_cfl(game: dict) -> ScheduledGame:
        game["id"] = str(game["game_id"])

        game["score"] = {
            "away": game["team_1"]["score"],
            "home": game["team_2"]["score"],
        }

        game["teams"] = {
            "away": {
                "id": game["team_1"]["team_id"],
                "location": game["team_1"]["location"],
                "name": game["team_1"]["nickname"],
                "abbreviation": game["team_1"]["abbreviation"],
            },

            "home": {
                "id": game["team_2"]["team_id"],
                "location": game["team_2"]["location"],
                "name": game["team_2"]["nickname"],
                "abbreviation": game["team_2"]["abbreviation"],
            },
        }

        game_entity = ScheduledGame(**game)
        game_entity.calculate_hash()

        return game_entity
