from __future__ import annotations

from yards_py.domain.entities.player_league_game_score import PlayerLeagueGameScore
from yards_py.domain.entities.player_season import PlayerSeason
from yards_py.domain.entities.scoring_settings import ScoringSettings
from typing import Dict, List, Optional
from yards_py.core.base_entity import BaseEntity
from yards_py.core.annotate_args import annotate_args


@annotate_args
class PlayerLeagueSeasonScore(BaseEntity):
    season: int
    player_id: str
    total_score: float
    average_score: float
    rank: Optional[int]
    game_scores: Dict[str, PlayerLeagueGameScore]
    last_week_score: Optional[float] = 0.0

    @staticmethod
    def create(id: str, player_season: PlayerSeason, scoring: ScoringSettings, completed_week: int) -> PlayerLeagueSeasonScore:
        season_score = scoring.calculate_score(player_season.stats)
        average = season_score.total_score / player_season.games_played if player_season.games_played else 0
        game_scores = {}

        last_week_score = 0.0

        for game in player_season.games:
            score = scoring.calculate_score(game.stats)
            game_score = PlayerLeagueGameScore(
                game_id=game.id,
                week_number=game.week_number,
                team=game.team,
                opponent=game.opponent,
                score=score,
            )
            game_scores[game.id] = game_score
            if game.week_number == completed_week:
                last_week_score = score.total_score

        return PlayerLeagueSeasonScore(
            id=id,
            player_id=player_season.player_id,
            season=player_season.season,
            total_score=season_score.total_score,
            average_score=average,
            game_scores=game_scores,
            last_week_score=last_week_score,
        )


def rank_player_seasons(player_season_scores: List[PlayerLeagueSeasonScore]):

    player_season_scores.sort(key=lambda x: x.total_score, reverse=True)

    rank = 0
    skip_by = 1
    last_player_score: PlayerLeagueSeasonScore = None
    for player_score in player_season_scores:
        tied = last_player_score and player_score.total_score == last_player_score.total_score

        if tied:
            player_score.rank = rank
            skip_by += 1
        else:
            rank += skip_by
            skip_by = 1
            player_score.rank = rank

        last_player_score = player_score
