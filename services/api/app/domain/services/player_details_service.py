

from typing import List, Optional

from fastapi import Depends
from pydantic import BaseModel
from yards_py.domain.entities.player import Player
from yards_py.domain.entities.player_league_season_score import \
    PlayerLeagueSeasonScore
from yards_py.domain.entities.player_score import PlayerScore
from yards_py.domain.entities.scoreboard import ScoreboardGame
from yards_py.domain.entities.stats import Stats
from yards_py.domain.entities.team import Team

from services.api.app.domain.repositories.game_repository import (
    GameRepository, create_game_repository)
from services.api.app.domain.repositories.player_game_repository import (
    PlayerGameRepository, create_player_game_repository)
from services.api.app.domain.repositories.player_league_season_score_repository import (
    PlayerLeagueSeasonScoreRepository,
    create_player_league_season_score_repository)
from services.api.app.domain.repositories.player_repository import (
    PlayerRepository, create_player_repository)
from services.api.app.domain.repositories.player_season_repository import (
    PlayerSeasonRepository, create_player_season_repository)


class GameLog(BaseModel):
    game_id: int
    game_number: int
    game: ScoreboardGame
    week: int
    season: int
    team: Team
    opponent: Team
    stats: Stats
    score: PlayerScore


class PlayerDetails(BaseModel):
    player: Player
    season_stats: Optional[Stats]
    season_score: Optional[PlayerLeagueSeasonScore]
    game_log: List[GameLog] = []


def create_player_details_service(
    player_repo: PlayerRepository = Depends(create_player_repository),
    score_repo: PlayerLeagueSeasonScoreRepository = Depends(create_player_league_season_score_repository),
    game_repo: GameRepository = Depends(create_game_repository),
    player_game_repo: PlayerGameRepository = Depends(create_player_game_repository),
    player_season_repo: PlayerSeasonRepository = Depends(create_player_season_repository),
):
    return PlayerDetailsService(
        player_repo=player_repo,
        score_repo=score_repo,
        game_repo=game_repo,
        player_game_repo=player_game_repo,
        player_season_repo=player_season_repo,
    )


class PlayerDetailsService:
    def __init__(
        self,
        player_repo: PlayerRepository,
        score_repo: PlayerLeagueSeasonScoreRepository,
        game_repo: GameRepository,
        player_game_repo: PlayerGameRepository,
        player_season_repo: PlayerSeasonRepository,
    ):
        self.player_repo = player_repo
        self.score_repo = score_repo
        self.game_repo = game_repo
        self.player_game_repo = player_game_repo
        self.player_season_repo = player_season_repo

    def get_player_details(self, season: int, league_id: str, player_id: str) -> Optional[PlayerDetails]:
        player = self.player_repo.get(season, player_id)

        if not player:
            return None

        player_season = self.player_season_repo.get(season, player_id)
        season_score = self.score_repo.get(league_id, player_id)

        season_stats = None
        if player_season:
            season_stats = player_season.stats

        details = PlayerDetails(
            player=player,
            season_stats=season_stats,
            season_score=season_score,
        )
        if season_score:
            for game_score in season_score.game_scores.values():
                player_game_id = game_score.game_id
                player_game = self.player_game_repo.get(season, player_game_id)
                game = self.game_repo.get(season, player_game.game_id)

                log = GameLog(
                    game_id=game.id,
                    game_number=game.game_number,
                    game=ScoreboardGame.create_from_game(game),
                    week=game.week,
                    season=season,
                    team=player_game.team,
                    opponent=player_game.opponent,
                    stats=player_game.stats,
                    score=game_score.score,
                )
                details.game_log.append(log)

        if details.game_log:
            details.game_log.sort(key=lambda x: x.game_number)

        return details
