

from app.yards_py.core.firestore_proxy import Query
from app.yards_py.domain.entities.player_season import PlayerSeason
from app.yards_py.domain.repositories.player_game_repository import PlayerGameRepository, create_player_game_repository
from app.yards_py.domain.repositories.player_season_repository import PlayerSeasonRepository, create_player_season_repository
from typing import List
from app.yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository
from fastapi import Depends
from app.yards_py.core.annotate_args import annotate_args
from app.yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor


def create_recalc_season_stats_command_executor(
    public_repo: PublicRepository = Depends(create_public_repository),
    player_game_repo: PlayerGameRepository = Depends(create_player_game_repository),
    player_season_repo: PlayerSeasonRepository = Depends(create_player_season_repository),
):
    return RecalcSeasonStatsCommandExecutor(
        public_repo=public_repo,
        player_game_repo=player_game_repo,
        player_season_repo=player_season_repo
    )


@annotate_args
class RecalcSeasonStatsCommand(BaseCommand):
    completed_week_number: int


@annotate_args
class RecalcSeasonStatsResult(BaseCommandResult[RecalcSeasonStatsCommand]):
    updated_players: List[PlayerSeason]


class RecalcSeasonStatsCommandExecutor(BaseCommandExecutor[RecalcSeasonStatsCommand, RecalcSeasonStatsResult]):
    def __init__(
        self,
        public_repo: PublicRepository,
        player_game_repo: PlayerGameRepository,
        player_season_repo: PlayerSeasonRepository
    ):
        self.public_repo = public_repo
        self.player_game_repo = player_game_repo
        self.player_season_repo = player_season_repo

    def on_execute(self, command: RecalcSeasonStatsCommand) -> RecalcSeasonStatsResult:

        state = self.public_repo.get_state()

        query = Query("week_number", "==", command.completed_week_number)
        player_games = self.player_game_repo.where(state.current_season, query)

        updated_players = list()

        # loop through all players who played this week, and only update them.
        for player_game in player_games:
            week_query = Query("week_number", "<", command.completed_week_number)
            player_query = Query("player_id", "==", player_game.player_id)
            prior_games = self.player_game_repo.where(state.current_season, [week_query, player_query])

            player_games = prior_games + [player_game]
            player_season = PlayerSeason.create(state.current_season, player_game.player_id, player_games)
            updated_players.append(player_season)

            self.player_season_repo.set(state.current_season, player_season)

        return RecalcSeasonStatsResult(command=command, updated_players=updated_players)
