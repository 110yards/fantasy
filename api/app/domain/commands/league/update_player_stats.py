
# from api.app.domain.entities.league_player_score import LeaguePlayerScore
from api.app.domain.entities.game_player_stats import GamePlayerStats
from api.app.domain.entities.player import PlayerLeagueSeasonScore
from api.app.domain.repositories.player_league_season_score_repository import PlayerLeagueSeasonScoreRepository, create_player_league_season_score_repository
from typing import Optional
from api.app.domain.repositories.state_repository import StateRepository, create_state_repository
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from api.app.core.annotate_args import annotate_args
from api.app.core.base_command_executor import (BaseCommand, BaseCommandExecutor,
                                                BaseCommandResult)
from fastapi.param_functions import Depends
from firebase_admin import firestore


def create_update_player_stats_command_executor(
    state_repo: StateRepository = Depends(create_state_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    league_player_score_repo: PlayerLeagueSeasonScoreRepository = Depends(create_player_league_season_score_repository),
):
    return UpdatePlayerStatsCommandExecutor(
        state_repo=state_repo,
        league_config_repo=league_config_repo,
        league_player_score_repo=league_player_score_repo)


@annotate_args
class UpdatePlayerStatsCommand(BaseCommand):
    league_id: Optional[str]
    game_id: str
    player_stats: GamePlayerStats


@annotate_args
class UpdatePlayerStatsResult(BaseCommandResult[UpdatePlayerStatsCommand]):
    pass


class UpdatePlayerStatsCommandExecutor(BaseCommandExecutor[UpdatePlayerStatsCommand, UpdatePlayerStatsResult]):

    def __init__(
        self,
        state_repo: StateRepository,
        league_config_repo: LeagueConfigRepository,
        league_player_score_repo: PlayerLeagueSeasonScoreRepository,
    ):
        self.state_repo = state_repo
        self.league_config_repo = league_config_repo
        self.league_player_score_repo = league_player_score_repo

    def on_execute(self, command: UpdatePlayerStatsCommand) -> UpdatePlayerStatsResult:

        player_id = command.player_stats.player.id
        game_id = command.game_id

        # recalc league score for player
        # outside the transaction, because we don't need to lock the league - scoring stats can't change while the season is running
        scoring = self.league_config_repo.get_scoring_config(command.league_id)
        stats = command.player_stats.stats
        new_score = scoring.calculate_score(stats)

        @firestore.transactional
        def update_player(transaction):
            player_score = self.league_player_score_repo.get(command.league_id, player_id, transaction)

            if not player_score:
                player_score = PlayerLeagueSeasonScore(id=player_id)

            player_score.game_scores[game_id] = new_score
            player_score.game_stats[game_id] = stats

            # update the player scores list for the league (player id + stats, not updated when player details change)
            self.league_player_score_repo.set(command.league_id, player_score, transaction)

            return UpdatePlayerStatsResult(command=command)

        transaction = self.league_player_score_repo.firestore.create_transaction()
        return update_player(transaction)
