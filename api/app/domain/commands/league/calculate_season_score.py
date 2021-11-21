
from api.app.config.config import Settings, get_settings
from api.app.core.logging import Logger
from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository
from api.app.domain.repositories.player_repository import PlayerRepository, create_player_repository
from api.app.domain.entities.league_player_score import LeaguePlayerScore
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
    settings: Settings = Depends(get_settings),
):
    return CalculateSeasonScoreCommandExecutor(league_config_repo, player_score_repo, player_repo, public_repo, settings)


@annotate_args
class CalculateSeasonScoreCommand(BaseCommand):
    league_id: Optional[str]


@annotate_args
class CalculateSeasonScoreResult(BaseCommandResult[CalculateSeasonScoreCommand]):
    scores: Optional[List]


class CalculateSeasonScoreCommandExecutor(BaseCommandExecutor[CalculateSeasonScoreCommand, CalculateSeasonScoreResult]):
    def __init__(
        self,
        league_config_repo: LeagueConfigRepository,
        player_score_repo: LeaguePlayerScoreRepository,
        player_repo: PlayerRepository,
        public_repo: PublicRepository,
        settings: Settings,
    ):
        self.league_config_repo = league_config_repo
        self.player_score_repo = player_score_repo
        self.player_repo = player_repo
        self.public_repo = public_repo
        self.settings = settings

    def on_execute(self, command: CalculateSeasonScoreCommand) -> CalculateSeasonScoreResult:

        season = self.settings.current_season

        if self.public_repo.get_switches().enable_score_testing:
            season = 2019
            Logger.warn("SCORE TESTING SWITCH IS ENABLED")

        players = self.player_repo.get_all(season)
        # players = [self.player_repo.get(season, "156305", transaction)]
        player_scores = self.player_score_repo.get_all(command.league_id)
        scoring = self.league_config_repo.get_scoring_config(command.league_id)

        player_scores = {player_score.id: player_score for player_score in player_scores}

        for player in players:
            player_score = player_scores.get(player.id, None)

            if not player_score:
                player_score = LeaguePlayerScore(id=player.id, game_stats=player.game_stats or {})
                player_scores[player.id] = player_score
                for game_id in player_score.game_stats:
                    game = player_score.game_stats[game_id]
                    player_score.game_scores[game_id] = scoring.calculate_score(game)

            player_score.season_stats = player.season_stats
            player_score.season_score = scoring.calculate_score(player.season_stats)

            player_score.games_played = len(player_score.game_stats)
            player_score.average = player_score.season_score.total_score / player_score.games_played if player_score.games_played > 0 else 0

        players = {player.id: player for player in players}
        player_scores = list(player_scores.values())
        player_scores.sort(key=lambda x: x.season_score.total_score, reverse=True)

        rank = 0
        skip_by = 1
        last_player_score: LeaguePlayerScore = None

        for player_score in player_scores:
            tied = last_player_score and player_score.season_score.total_score == last_player_score.season_score.total_score

            if tied:
                player_score.rank = rank
                skip_by += 1
            else:
                rank += skip_by
                skip_by = 1
                player_score.rank = rank

            last_player_score = player_score

        for player_score in player_scores:
            self.player_score_repo.set(command.league_id, player_score)

        result_scores = [
            {
                "id": score.id,
                "player": players[score.id].display_name,
                "score": score.season_score.total_score,
                "rank": score.rank,

            } for score in player_scores]

        return CalculateSeasonScoreResult(command=command, scores=result_scores)
