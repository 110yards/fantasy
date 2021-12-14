from __future__ import annotations

from api.app.domain.entities.player import PlayerSeason
from api.app.domain.entities.player_score import PlayerScore
from api.app.domain.entities.scoring_settings import ScoringSettings
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

    @staticmethod
    def create(id: str, player_season: PlayerSeason, scoring: ScoringSettings) -> LeaguePlayerScore:
        score = scoring.calculate_score(player_season.stats)
        average = score.total_score / player_season.games_played if player_season.games_played else 0

        return LeaguePlayerScore(
            id=id,
            player_id=player_season.player_id,
            season=player_season.season,
            total_score=score.total_score,
            average_score=average
        )
