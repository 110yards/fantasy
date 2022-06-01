from enum import Enum


class LeagueCommandType(str, Enum):
    UPDATE_PLAYER = "update_player"
    UPDATE_PLAYER_STATS = "update_player_stats"
    CALCULATE_PLAYOFFS = "calculate_playoffs"
    CALCULATE_RESULTS = "calculate_results"
    CALCULATE_SEASON_SCORE = "calculate_season_score"
    PROCESS_WAIVERS = "process_waivers"
