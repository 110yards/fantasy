from __future__ import annotations

from yards_py.core.logging import Logger
from yards_py.domain.entities.player_game import PlayerGame

from yards_py.domain.entities.boxscore import Boxscore

from yards_py.domain.entities.game import Game
from yards_py.domain.repositories.player_game_repository import PlayerGameRepository, create_player_game_repository

from ....api_proxies.core.core_game_proxy import CoreGameProxy, create_core_game_proxy


from ....api_proxies.core.core_scoreboard_proxy import CoreScoreboardProxy, create_core_scoreboard_proxy
from yards_py.domain.entities.scoreboard import Scoreboard, ScoreboardGame
from yards_py.domain.entities.state import Locks
from yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository


from yards_py.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult

from fastapi.param_functions import Depends

from firebase_admin import firestore




class ManualUpdateGameCommand(BaseCommand):
    game_id: int


class ManualUpdateGameResult(BaseCommandResult):
    pass


class ManualUpdateGameCommandExecutor(BaseCommandExecutor[ManualUpdateGameCommand, ManualUpdateGameResult]):
    def __init__(
        self,
        proxy: CoreGameProxy,
        player_game_repo: PlayerGameRepository,
        public_repo: PublicRepository,
    ):
        self.proxy = proxy
        self.player_game_repo = player_game_repo
        self.public_repo = public_repo

    def on_execute(self, command: ManualUpdateGameCommand) -> ManualUpdateGameResult:
        data = self.proxy.get_game(command.game_id)
        state = self.public_repo.get_state()
        
        boxscore = Boxscore(**data)

        player_games = []

        for away_stats in boxscore.teams.away_stats:
            player_game = PlayerGame(
                player_id=away_stats.player_id,
                game_id=away_stats.game_id,
                week_number=away_stats.week,
                team=away_stats.team,
                opponent=away_stats.opponent,
                stats=away_stats.stats,
                date_updated=away_stats.date_updated,
            )
            player_game.set_id()
            player_games.append(player_game)

        for home_stats in boxscore.teams.home_stats:
            player_game = PlayerGame(
                player_id=home_stats.player_id,
                game_id=home_stats.game_id,
                week_number=home_stats.week,
                team=home_stats.team,
                opponent=home_stats.opponent,
                stats=home_stats.stats,
                date_updated=home_stats.date_updated,
            )
            player_game.set_id()
            player_games.append(player_game)

        @firestore.transactional
        def update(transaction, player_game: PlayerGame) -> None:
            existing = self.player_game_repo.get(state.current_season, player_game.id, transaction)

            if player_game.id == None:
                raise Exception("Player game id is None")

            needs_update = not existing or not existing.date_updated or existing.date_updated < player_game.date_updated

            if not needs_update:
                return None
            
            Logger.info(f"Updating player game: {player_game.id}")
            
            self.player_game_repo.set(state.current_season, player_game, transaction)

            return player_game
        
        for player_game in player_games:
            transaction = self.public_repo.firestore.create_transaction()
            update(transaction, player_game)

        return ManualUpdateGameResult(command=command)


def create_manual_update_game_command_executor(
    proxy: CoreGameProxy = Depends(create_core_game_proxy),
    player_game_repo: PlayerGameRepository = Depends(create_player_game_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return ManualUpdateGameCommandExecutor(
        proxy=proxy,
        player_game_repo=player_game_repo,
        public_repo=public_repo,
    )
