

from yards_py.core.base_entity import BaseEntity


class PlayerScore(BaseEntity):
    pass_attempts: float
    pass_completions: float
    pass_net_yards: float
    # pass_long: float
    pass_touchdowns: float
    pass_interceptions: float
    pass_fumbles: float
    rush_attempts: float
    rush_net_yards: float
    # rush_long: float
    rush_touchdowns: float
    # rush_long_touchdowns: float
    # receive_attempts: float
    receive_caught: float
    receive_yards: float
    # receive_long: float
    receive_touchdowns: float
    # receive_long_touchdowns: float
    # receive_yards_after_catch: float
    receive_fumbles: float
    # punts: float
    # punt_yards: float
    # punt_net_yards: float
    # punt_long: float
    punt_singles: float
    # punts_blocked: float
    # punts_in_10: float
    # punts_in_20: float
    # punts_returned: float
    # kick_returns: float
    kick_returns_yards: float
    kick_returns_touchdowns: float
    # kick_returns_long: float
    # kick_returns_touchdowns_long: float
    # field_goal_attempts: float
    field_goal_made: float
    field_goal_misses: float
    # field_goal_yards: float
    field_goal_singles: float
    # field_goal_long: float
    # field_goal_points: float
    # field_goal_returns: float
    field_goal_returns_yards: float
    field_goal_returns_touchdowns: float
    # field_goal_returns_long: float
    # field_goal_returns_touchdowns_long: float
    # punt_returns: float
    punt_returns_yards: float
    punt_returns_touchdowns: float
    # punt_returns_long: float
    # punt_returns_touchdowns_long: float
    # kicks: float
    # kick_yards: float
    # kicks_net_yards: float
    # kicks_long: float
    kicks_singles: float
    # kicks_out_of_end_zone: float
    # kicks_onside: float
    # one_point_converts_attempts: float
    one_point_converts_made: float
    two_point_converts_made: float
    # tackles_total: float
    tackles_defensive: float
    tackles_special_teams: float
    sacks_qb_made: float
    interceptions: float
    fumbles_forced: float
    fumbles_recovered: float
    passes_knocked_down: float
    total_score: float
