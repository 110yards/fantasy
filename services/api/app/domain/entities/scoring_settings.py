from __future__ import annotations

import hashlib
import json
from decimal import getcontext

from pydantic import BaseModel

from app.domain.entities.player_score import PlayerScore
from app.domain.entities.stats import Stats


class ScoringSettings(BaseModel):
    pass_attempts: float
    pass_completions: float
    pass_net_yards: float
    pass_touchdowns: float
    pass_interceptions: float
    pass_fumbles: float  # This is a fumble by the QB (eg after a sack or fumbled snap)
    rush_net_yards: float
    rush_attempts: float
    rush_touchdowns: float
    rush_long_touchdowns: float
    receive_caught: float
    receive_yards: float
    receive_touchdowns: float
    receive_fumbles: float  # This is a fumble by the receiver after a catch and run
    punt_singles: float
    kick_returns_yards: float
    kick_returns_touchdowns: float
    field_goal_made: float
    field_goal_misses: float
    field_goal_singles: float
    field_goal_returns_yards: float
    field_goal_returns_touchdowns: float
    punt_returns_yards: float
    punt_returns_touchdowns: float
    kicks_singles: float
    one_point_converts_made: float
    two_point_converts_made: float
    tackles_defensive: float
    tackles_special_teams: float
    sacks_qb_made: float
    interceptions: float
    fumbles_forced: float
    fumbles_recovered: float
    passes_knocked_down: float
    id: str = "scoring"

    @property
    def hash(self) -> str:
        return hashlib.md5(json.dumps(self.dict()).encode("utf-8")).hexdigest()

    @staticmethod
    def create_default() -> ScoringSettings:
        settings = ScoringSettings.model_construct()

        getcontext().prec = 1

        # Passing
        settings.pass_attempts = 0
        settings.pass_touchdowns = 4
        settings.pass_net_yards = 0.04
        settings.pass_interceptions = -2
        settings.pass_completions = 0
        settings.pass_fumbles = -2

        # Rushing
        settings.rush_touchdowns = 6
        settings.rush_net_yards = 0.1
        settings.rush_attempts = 0
        settings.rush_long_touchdowns = 0

        # Receiving
        settings.receive_touchdowns = 6
        settings.receive_yards = 0.1
        settings.receive_caught = 0

        # General offense
        settings.two_point_converts_made = 2
        settings.receive_fumbles = -2  # rushing fumbles are included here, see John Santiago (164764) game 2559
        # settings.fumbles_lost = -2 # Not available in game API

        # Special Teams Returns
        settings.kick_returns_touchdowns = 6
        settings.punt_returns_touchdowns = 6
        settings.field_goal_returns_touchdowns = 6
        settings.kick_returns_yards = 0
        settings.field_goal_returns_yards = 0
        settings.punt_returns_yards = 0

        # Kicking
        settings.one_point_converts_made = 1
        settings.field_goal_made = 3
        settings.field_goal_misses = -1
        settings.field_goal_singles = 1
        settings.punt_singles = 1
        settings.kicks_singles = 1

        # Defense
        settings.tackles_defensive = 1
        settings.tackles_special_teams = 0
        settings.sacks_qb_made = 2
        settings.interceptions = 3
        settings.fumbles_forced = 3
        settings.fumbles_recovered = 3
        settings.passes_knocked_down = 2
        # settings.defensive_touchdowns = 6 # Not available in game API
        # settings.safeties = 2 # Not available in game API

        return settings

    @staticmethod
    def create_ppr() -> ScoringSettings:
        settings = ScoringSettings.create_default()
        settings.receive_caught = 0.5

        return settings

    @staticmethod
    def create_admins_choice() -> ScoringSettings:
        settings = ScoringSettings.model_construct()

        getcontext().prec = 1

        # Passing
        settings.pass_touchdowns = 4
        settings.pass_net_yards = 0.05
        settings.pass_interceptions = -2
        settings.pass_completions = 0
        settings.pass_fumbles = -2

        # Rushing
        settings.rush_touchdowns = 6
        settings.rush_net_yards = 0.1
        settings.rush_attempts = 0
        # settings.rush_long_touchdowns = 0

        # Receiving
        settings.receive_touchdowns = 6
        settings.receive_yards = 0.1
        settings.receive_caught = 1

        # General offense
        settings.two_point_converts_made = 2
        settings.receive_fumbles = -2  # rushing fumbles are included here, see John Santiago (164764) game 2559
        # settings.fumbles_lost = -2 # Not available in game API

        # Special Teams Returns
        settings.kick_returns_touchdowns = 6
        settings.punt_returns_touchdowns = 6
        settings.field_goal_returns_touchdowns = 6
        settings.kick_returns_yards = 0.05
        settings.field_goal_returns_yards = 0.05
        settings.punt_returns_yards = 0.05

        # Kicking
        settings.one_point_converts_made = 1
        settings.field_goal_made = 2
        settings.field_goal_misses = -1
        settings.field_goal_singles = 1
        settings.punt_singles = 1
        settings.kicks_singles = 1

        # Defense
        settings.tackles_defensive = 2
        settings.tackles_special_teams = 2
        settings.sacks_qb_made = 3
        settings.interceptions = 5
        settings.fumbles_forced = 2
        settings.fumbles_recovered = 3
        settings.passes_knocked_down = 1
        # settings.defensive_touchdowns = 6 # Not available in game API
        # settings.safeties = 2 # Not available in game API

        return settings

    def calculate_score(self, stats: Stats) -> PlayerScore:
        score = PlayerScore.model_construct(total_score=0)

        keys = self.dict(exclude={"id": ...})
        for key in keys:
            if key not in PlayerScore.__fields__.keys():  # don't include this state if we don't score it
                continue
            stat = getattr(stats, key, 0)
            value = getattr(self, key)
            stat_score = stat * value if stat else 0

            setattr(score, key, round(stat_score, 2))
            score.total_score += stat_score

        score.total_score = round(score.total_score, 2)
        return score
