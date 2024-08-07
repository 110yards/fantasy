from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Stats(BaseModel):
    pass_attempts: Optional[int]
    pass_completions: Optional[int]
    pass_net_yards: Optional[int]
    pass_long: Optional[int]
    pass_touchdowns: Optional[int]
    # pass_completion_percentage: Optional[str]
    # pass_efficiency: Optional[str]
    pass_interceptions: Optional[int]
    pass_fumbles: Optional[int]
    rush_attempts: Optional[int]
    rush_net_yards: Optional[int]
    rush_long: Optional[int]
    rush_touchdowns: Optional[int]
    rush_long_touchdowns: Optional[int]
    receive_attempts: Optional[int]
    receive_caught: Optional[int]
    receive_yards: Optional[int]
    receive_long: Optional[int]
    receive_touchdowns: Optional[int]
    receive_long_touchdowns: Optional[int]
    receive_yards_after_catch: Optional[int]
    receive_fumbles: Optional[int]
    punts: Optional[int]
    punt_yards: Optional[int]
    punt_gross_yards: Optional[int]
    punt_net_yards: Optional[int]
    punt_long: Optional[int]
    punt_singles: Optional[int]
    punts_blocked: Optional[int]
    punts_in_10: Optional[int]
    punts_in_20: Optional[int]
    punts_returned: Optional[int]
    kick_returns: Optional[int]
    kick_returns_yards: Optional[int]
    kick_returns_touchdowns: Optional[int]
    kick_returns_long: Optional[int]
    kick_returns_touchdowns_long: Optional[int]
    field_goal_attempts: Optional[int]
    field_goal_made: Optional[int]
    field_goal_misses: Optional[int]
    field_goal_yards: Optional[int]
    field_goal_singles: Optional[int]
    field_goal_long: Optional[int]
    field_goal_points: Optional[int]
    field_goal_returns: Optional[int]
    field_goal_returns_yards: Optional[int]
    field_goal_returns_touchdowns: Optional[int]
    field_goal_returns_long: Optional[int]
    field_goal_returns_touchdowns_long: Optional[int]
    punt_returns: Optional[int]
    punt_returns_yards: Optional[int]
    punt_returns_touchdowns: Optional[int]
    punt_returns_long: Optional[int]
    punt_returns_touchdowns_long: Optional[int]
    kicks: Optional[int]
    kick_yards: Optional[int]
    kicks_net_yards: Optional[int]
    kicks_long: Optional[int]
    kicks_singles: Optional[int]
    kicks_out_of_end_zone: Optional[int]
    kicks_onside: Optional[int]
    one_point_converts_attempts: Optional[int]
    one_point_converts_made: Optional[int]
    two_point_converts_made: Optional[int]
    tackles_total: Optional[int]
    tackles_defensive: Optional[int]
    tackles_special_teams: Optional[int]
    sacks_qb_made: Optional[int]
    interceptions: Optional[int]
    fumbles_forced: Optional[int]
    fumbles_recovered: Optional[int]
    passes_knocked_down: Optional[int]
