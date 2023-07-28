from __future__ import annotations

from pydantic import BaseModel


class ScoringInfo(BaseModel):
    id: str = "scoring_info"
    sections: list[dict] = [
        {
            "description": "Passing",
            "actions": [
                {"id": "pass_attempts", "description": "Attempts"},
                {"id": "pass_completions", "description": "Completions"},
                {
                    "id": "pass_net_yards",
                    "description": "Yards (net)",
                    "show_yards_per_point": True,
                },
                {"id": "pass_touchdowns", "description": "Touchdowns"},
                {"id": "pass_interceptions", "description": "Interceptions"},
                # This is a fumble by the QB (eg after a sack or fumbled snap)
                # {"id": "pass_fumbles", "description": "QB Fumbles"},
            ],
        },
        {
            "description": "Rushing",
            "actions": [
                {
                    "id": "rush_net_yards",
                    "description": "Yards (net)",
                    "show_yards_per_point": True,
                },
                {"id": "rush_attempts", "description": "Rushes"},
                {"id": "rush_touchdowns", "description": "Touchdowns"},
                # {"id": "rush_long_touchdowns", "description": "Rushing longest touchdown"},
            ],
        },
        {
            "description": "Receiving",
            "actions": [
                {"id": "receive_caught", "description": "Receptions"},
                {
                    "id": "receive_yards",
                    "description": "Yards",
                    "show_yards_per_point": True,
                },
                {"id": "receive_touchdowns", "description": "Touchdowns"},
            ],
        },
        {
            "description": "Offense",
            "actions": [
                {"id": "receive_fumbles", "description": "Fumbles"},  # This is a fumble after a catch and run or after a rush
                {"id": "two_point_converts_made", "description": "Two point converts"},
            ],
        },
        {
            "description": "Kicking",
            "actions": [
                {"id": "punt_singles", "description": "Punt/kick-off singles"},
                # {"id": "kicks_singles", "description": "Kick-off singles"},
                {"id": "field_goal_made", "description": "Field goal made"},
                {"id": "field_goal_misses", "description": "Field goal misses"},
                {"id": "field_goal_singles", "description": "Field goal singles"},
                {"id": "one_point_converts_made", "description": "One point converts"},
            ],
        },
        {
            "description": "Kick Returning",
            "actions": [
                {
                    "id": "kick_returns_yards",
                    "description": "Yards",
                    "show_yards_per_point": True,
                },
                {"id": "kick_returns_touchdowns", "description": "Touchdowns"},
                # {"id": "field_goal_returns_yards", "description": "FG miss return yards"},
                # {"id": "field_goal_returns_touchdowns", "description": "FG miss return touchdowns"},
                # {"id": "punt_returns_yards", "description": "Punt return yards"},
                # {"id": "punt_returns_touchdowns", "description": "Punt return touchdowns"},
            ],
        },
        {
            "description": "Defense",
            "actions": [
                {"id": "tackles_defensive", "description": "Tackles"},
                {"id": "tackles_special_teams", "description": "Special teams tackles"},
                {"id": "sacks_qb_made", "description": "Sacks"},
                {"id": "interceptions", "description": "Interceptions"},
                {"id": "fumbles_forced", "description": "Fumbles forced"},
                {"id": "fumbles_recovered", "description": "Fumbles recovered"},
                {"id": "passes_knocked_down", "description": "Passes knocked down"},
            ],
        },
    ]
