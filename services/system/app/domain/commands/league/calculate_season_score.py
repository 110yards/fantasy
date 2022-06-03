

from yards_py.domain.entities.player_league_season_score import PlayerLeagueSeasonScore, rank_player_seasons
from yards_py.domain.repositories.player_season_repository import PlayerSeasonRepository, create_player_season_repository
from yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository
from yards_py.domain.repositories.player_repository import PlayerRepository, create_player_repository
from yards_py.domain.repositories.player_league_season_score_repository import PlayerLeagueSeasonScoreRepository, create_player_league_season_score_repository
from yards_py.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from typing import List, Optional
from fastapi import Depends
from yards_py.core.annotate_args import annotate_args
from yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor


def create_calculate_season_score_command_executor(
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    player_score_repo: PlayerLeagueSeasonScoreRepository = Depends(create_player_league_season_score_repository),
    player_repo: PlayerRepository = Depends(create_player_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
    player_season_repo: PlayerSeasonRepository = Depends(create_player_season_repository),
):
    return CalculateSeasonScoreCommandExecutor(league_config_repo, player_score_repo, player_repo, public_repo, player_season_repo)


@annotate_args
class CalculateSeasonScoreCommand(BaseCommand):
    league_id: Optional[str]
    season: Optional[int]


@annotate_args
class CalculateSeasonScoreResult(BaseCommandResult[CalculateSeasonScoreCommand]):
    pass


class CalculateSeasonScoreCommandExecutor(BaseCommandExecutor[CalculateSeasonScoreCommand, CalculateSeasonScoreResult]):
    def __init__(
        self,
        league_config_repo: LeagueConfigRepository,
        player_score_repo: PlayerLeagueSeasonScoreRepository,
        player_repo: PlayerRepository,
        public_repo: PublicRepository,
        player_season_repo: PlayerSeasonRepository,
    ):
        self.league_config_repo = league_config_repo
        self.player_score_repo = player_score_repo
        self.player_repo = player_repo
        self.public_repo = public_repo
        self.player_season_repo = player_season_repo

    def on_execute(self, command: CalculateSeasonScoreCommand) -> CalculateSeasonScoreResult:

        state = self.public_repo.get_state()
        season = command.season or state.current_season
        completed_week = state.current_week - 1

        players_seasons = self.player_season_repo.get_all(season)

        scoring = self.league_config_repo.get_scoring_config(command.league_id)

        if not scoring:
            return CalculateSeasonScoreResult(command=command, error="League not found")

        player_season_scores: List[PlayerLeagueSeasonScore] = list()

        for player_season in players_seasons:
            player_season_score = PlayerLeagueSeasonScore.create(player_season.id, player_season, scoring, completed_week)
            player_season_scores.append(player_season_score)

        rank_player_seasons(player_season_scores)

        for player_score in player_season_scores:
            self.player_score_repo.set(command.league_id, player_score)

        return CalculateSeasonScoreResult(command=command)
