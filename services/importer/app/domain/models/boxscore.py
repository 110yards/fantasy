from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, computed_field


class BoxscorePlayer(BaseModel):
    first_name: str
    last_name: str
    player_id: str = None
    team_abbr: str


class PlayerStats(BaseModel):
    player: BoxscorePlayer

    pass_attempts: int = 0
    pass_completions: int = 0
    pass_net_yards: int = 0
    pass_touchdowns: int = 0
    pass_interceptions: int = 0
    pass_fumbles: int = 0
    pass_long: int = 0

    rush_attempts: int = 0
    rush_net_yards: int = 0
    rush_touchdowns: int = 0
    rush_long: int = 0
    rush_long_touchdowns: int = 0

    receive_caught: int = 0
    receive_yards: int = 0
    receive_long: int = 0
    receive_touchdowns: int = 0
    receive_attempts: int = 0
    receive_long_touchdowns: int = 0
    receive_yards_after_catch: int = 0
    receive_fumbles: int = 0

    punts: int = 0
    punt_yards: int = 0
    punt_long: int = 0
    punt_net_yards: int = 0
    punt_singles: int = 0
    punts_blocked: int = 0
    punts_in_10: int = 0
    punts_in_20: int = 0
    punts_returned: int = 0

    punt_returns: int = 0
    punt_returns_yards: int = 0
    punt_returns_touchdowns: int = 0
    punt_returns_long: int = 0
    punt_returns_touchdowns_long: int = 0

    kick_returns: int = 0
    kick_returns_yards: int = 0
    kick_returns_touchdowns: int = 0
    kick_returns_long: int = 0
    kick_returns_touchdowns_long: int = 0

    field_goal_attempts: int = 0
    field_goal_made: int = 0
    field_goal_yards: int = 0
    field_goal_singles: int = 0
    field_goal_long: int = 0
    field_goal_points: int = 0

    field_goal_returns: int = 0
    field_goal_returns_yards: int = 0
    field_goal_returns_touchdowns: int = 0
    field_goal_returns_long: int = 0
    field_goal_returns_touchdowns_long: int = 0

    kicks: int = 0
    kicks_singles: int = 0
    kick_yards: int = 0
    kicks_net_yards: int = 0
    kicks_long: int = 0
    kicks_out_of_end_zone: int = 0
    kicks_onside: int = 0

    one_point_converts_attempts: int = 0
    one_point_converts_made: int = 0
    two_point_converts_made: int = 0

    tackles_defensive: int = 0
    tackles_special_teams: int = 0
    sacks_qb_made: int = 0
    interceptions: int = 0
    fumbles_forced: int = 0
    fumbles_recovered: int = 0
    passes_knocked_down: int = 0
    tackles_for_loss: int = 0

    @computed_field
    @property
    def tackles_total(self) -> int:
        return self.tackles_defensive + self.tackles_special_teams


StatsCollection = dict[str, PlayerStats]


class Boxscore(BaseModel):
    source: Literal["realtime", "official"]
    game_id: str
    away_abbr: str
    home_abbr: str
    player_stats: StatsCollection = {}
    unmatched_player_stats: StatsCollection = {}

    def hash(self) -> str:
        return hashlib.md5(self.model_dump_json().encode("utf-8")).hexdigest()
