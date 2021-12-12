
from api.app.domain.entities.player import PlayerLeagueSeasonScore
from api.app.domain.repositories.player_season_repository import PlayerSeasonRepository, create_player_season_repository
from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository
from api.app.domain.repositories.player_repository import PlayerRepository, create_player_repository
from api.app.domain.repositories.league_player_score_repository import LeaguePlayerScoreRepository, create_league_player_score_repository
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from typing import List, Optional
from fastapi import Depends
from api.app.core.annotate_args import annotate_args
from api.app.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor


def create_calculate_season_score_command_executor(
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    player_score_repo: LeaguePlayerScoreRepository = Depends(create_league_player_score_repository),
    player_repo: PlayerRepository = Depends(create_player_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
    player_season_repo: PlayerSeasonRepository = Depends(create_player_season_repository),
):
    return CalculateSeasonScoreCommandExecutor(league_config_repo, player_score_repo, player_repo, public_repo, player_season_repo)


@annotate_args
class CalculateSeasonScoreCommand(BaseCommand):
    league_id: Optional[str]


@annotate_args
class CalculateSeasonScoreResult(BaseCommandResult[CalculateSeasonScoreCommand]):
    pass


class CalculateSeasonScoreCommandExecutor(BaseCommandExecutor[CalculateSeasonScoreCommand, CalculateSeasonScoreResult]):
    def __init__(
        self,
        league_config_repo: LeagueConfigRepository,
        player_score_repo: LeaguePlayerScoreRepository,
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

        season = self.public_repo.get_state().current_season

        players_seasons = self.player_season_repo.get_all(season)

        scoring = self.league_config_repo.get_scoring_config(command.league_id)

        if not scoring:
            return CalculateSeasonScoreResult(command=command, error="League not found")

        player_season_scores: List[PlayerLeagueSeasonScore] = list()

        for player_season in players_seasons:
            # should I calculate the week's score too?
            player_season_score = PlayerLeagueSeasonScore.create(player_season.id, player_season, scoring)
            player_season_scores.append(player_season_score)

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

        for player_score in player_season_scores:
            raise NotImplementedError()  # TODO: make the repo for this.  Also maybe remove the PlayerScoreRepo?  Or repurpose?
            # self.player_score_repo.set(command.league_id, player_score)

        return CalculateSeasonScoreResult(command=command)
