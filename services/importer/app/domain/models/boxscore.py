from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class BoxscorePlayer(BaseModel):
    first_name: str
    last_name: str
    player_id: str = None
    birth_date: Optional[datetime] = None


class PlayerPassing(BaseModel):
    player: BoxscorePlayer
    pass_attempts: int
    pass_completions: int
    pass_net_yards: int
    pass_touchdowns: int
    pass_interceptions: int
    pass_fumbles: int = 0
    pass_long: int = 0


class PlayerRushing(BaseModel):
    player: BoxscorePlayer
    rush_attempts: int
    rush_net_yards: int
    rush_touchdowns: int
    rush_long: int = 0
    rush_long_touchdowns: int = 0


class PlayerReceiving(BaseModel):
    player: BoxscorePlayer
    receive_caught: int
    receive_yards: int
    receive_long: int
    receive_touchdowns: int
    receive_attempts: int = 0
    receive_long_touchdowns: int = 0
    receive_yards_after_catch: int = 0
    receive_fumbles: int = 0


class PlayerPunts(BaseModel):
    player: BoxscorePlayer
    punts: int
    punt_yards: int
    punt_long: int
    punt_net_yards: int = 0
    punt_singles: int = 0
    punts_blocked: int = 0
    punts_in_10: int = 0
    punts_in_20: int = 0
    punts_returned: int = 0


class PlayerPuntReturns(BaseModel):
    player: BoxscorePlayer
    punt_returns: int
    punt_returns_yards: int
    punt_returns_touchdowns: int
    punt_returns_long: int
    punt_returns_touchdowns_long: int = 0


class PlayerKickReturns(BaseModel):
    player: BoxscorePlayer
    kick_returns: int
    kick_returns_yards: int
    kick_returns_touchdowns: int
    kick_returns_long: int
    kick_returns_touchdowns_long: int = 0


class PlayerFieldGoals(BaseModel):
    player: BoxscorePlayer
    field_goal_attempts: int
    field_goal_made: int
    field_goal_yards: int = 0
    field_goal_singles: int = 0
    field_goal_long: int = 0
    field_goal_missed_list: str = 0
    field_goal_points: int = 0


class PlayerFieldGoalReturns(BaseModel):
    player: BoxscorePlayer
    field_goal_returns: int
    field_goal_returns_yards: int
    field_goal_returns_touchdowns: int
    field_goal_returns_long: int
    field_goal_returns_touchdowns_long: int


class PlayerKicking(BaseModel):
    player: BoxscorePlayer
    kicks: int
    kicks_singles: int
    kick_yards: int = 0
    kicks_net_yards: int = 0
    kicks_long: int = 0
    kicks_out_of_end_zone: int
    kicks_onside: int


class PlayerOnePointConverts(BaseModel):
    player: BoxscorePlayer
    one_point_converts_attempts: int
    one_point_converts_made: int


class PlayerTwoPointConverts(BaseModel):
    player: BoxscorePlayer
    two_point_converts_made: int


class PlayerDefence(BaseModel):
    player: BoxscorePlayer
    tackles_total: int = 0
    tackles_defensive: int
    tackles_special_teams: int = 0
    sacks_qb_made: int
    interceptions: int
    fumbles_forced: int
    fumbles_recovered: int = 0
    passes_knocked_down: int


class BoxscoreTeam(BaseModel):
    passing: Optional[List[PlayerPassing]] = None
    rushing: Optional[List[PlayerRushing]] = None
    receiving: Optional[List[PlayerReceiving]] = None
    punts: Optional[List[PlayerPunts]] = None
    punt_returns: Optional[List[PlayerPuntReturns]] = None
    kick_returns: Optional[List[PlayerKickReturns]] = None
    field_goals: Optional[List[PlayerFieldGoals]] = None
    field_goal_returns: Optional[List[PlayerFieldGoalReturns]] = None
    kicking: Optional[List[PlayerKicking]] = None
    one_point_converts: Optional[List[PlayerOnePointConverts]] = None
    two_point_converts: Optional[List[PlayerTwoPointConverts]] = None
    defence: Optional[List[PlayerDefence]] = None


class Boxscore(BaseModel):
    away_abbr: str
    home_abbr: str
    away_box: BoxscoreTeam
    home_box: BoxscoreTeam

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def hash(self) -> str:
        return hashlib.md5(json.dumps(self.json()).encode("utf-8")).hexdigest()
