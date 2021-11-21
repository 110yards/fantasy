

from api.app.domain.entities.player_score import PlayerScore
from api.app.domain.entities.stats import Stats
from typing import Dict, Optional
from api.app.core.base_entity import BaseEntity
from api.app.core.annotate_args import annotate_args


@annotate_args
class LeaguePlayerScore(BaseEntity):
    rank: Optional[int]

    season_stats: Optional[Stats]
    season_score: Optional[PlayerScore]
    average: Optional[float] = 0
    games_played: Optional[int] = 0

    game_scores: Dict[str, PlayerScore] = {}
    game_stats: Dict[str, Stats] = {}
