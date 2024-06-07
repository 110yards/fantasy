from __future__ import annotations
from datetime import datetime

from yards_py.domain.entities.stats import Stats

from yards_py.domain.entities.team import Team


from yards_py.domain.entities.player_game import PlayerGame
from yards_py.domain.repositories.player_game_repository import PlayerGameRepository, create_player_game_repository
from yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository


from yards_py.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult

from fastapi.param_functions import Depends

from firebase_admin import firestore
from pydantic import BaseModel

from yards_py.core.logging import Logger

class BoxscorePlayerStats(BaseModel):
    player_id: str
    game_id: str
    year: int
    week: int
    team: Team
    opponent: Team
    name: str
    date_updated: datetime
    stats: Stats


class UpdatePlayerStatsCommand(BaseCommand):
    player_boxscore: BoxscorePlayerStats


class UpdatePlayerStatsResult(BaseCommandResult):
    player_game: PlayerGame | None


class UpdatePlayerStatsCommandExecutor(BaseCommandExecutor[UpdatePlayerStatsCommand, UpdatePlayerStatsResult]):
    def __init__(
        self,
        public_repo: PublicRepository,
        player_game_repo: PlayerGameRepository,
    ):
        self.public_repo = public_repo
        self.player_game_repo = player_game_repo

    def on_execute(self, command: UpdatePlayerStatsCommand) -> UpdatePlayerStatsResult:
        state = self.public_repo.get_state()       

        # is this game for this year and week?
        if command.player_boxscore.year != state.current_season or command.player_boxscore.week != state.current_week:
            Logger.info(f"Game is not for current season/week: {command.player_boxscore.year}/{command.player_boxscore.week}, player stats will not be recorded")
            return UpdatePlayerStatsResult(command=command, player_game=None)

        player_game = PlayerGame(
            player_id=command.player_boxscore.player_id,
            game_id=command.player_boxscore.game_id,
            week_number=command.player_boxscore.week,
            team=command.player_boxscore.team,
            opponent=command.player_boxscore.opponent,
            stats=command.player_boxscore.stats,
            date_updated=command.player_boxscore.date_updated,
        )

        player_game.set_id()

        @firestore.transactional
        def update(transaction) -> PlayerGame | None:
            existing = self.player_game_repo.get(state.current_season, player_game.id, transaction)

            needs_update = not existing or existing.date_updated < player_game.date_updated

            if not needs_update:
                return None
            
            self.player_game_repo.set(state.current_season, player_game, transaction)

            return player_game


        transaction = self.public_repo.firestore.create_transaction()

        player_game = update(transaction)

        return UpdatePlayerStatsResult(command=command, player_game=player_game)


def create_update_player_stats_command_executor(
    public_repo: PublicRepository = Depends(create_public_repository),
    player_game_repo: PlayerGameRepository = Depends(create_player_game_repository),
):
    return UpdatePlayerStatsCommandExecutor(
        public_repo=public_repo,
        player_game_repo=player_game_repo,
    )
