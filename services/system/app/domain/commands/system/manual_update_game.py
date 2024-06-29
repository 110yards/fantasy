from __future__ import annotations

from .......yards_py.domain.repositories.player_game_repository import PlayerGameRepository

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
    scoreboard: Scoreboard | None


class ManualUpdateGameCommandExecutor(BaseCommandExecutor[ManualUpdateGameCommand, ManualUpdateGameResult]):
    def __init__(
        self,
        proxy: CoreGameProxy,
        player_game_repo: PlayerGameRepository,
    ):
        self.proxy = proxy
        self.player_game_repo = player_game_repo

    def on_execute(self, command: ManualUpdateGameCommand) -> ManualUpdateGameResult:

        
        # @firestore.transactional
        # def update(transaction) -> Scoreboard | None:
        #     state = self.public_repo.get_state(transaction)

        #     data = self.proxy.get_scoreboard(state.current_season, state.current_week)

        #     games = [ScoreboardGame(**x) for x in data["games"]]
        #     games = {x.game_id: x for x in games}
        #     scoreboard = Scoreboard(games=games)            

        #     locks = Locks.create_from_scoreboard(scoreboard)

        #     if locks.changed(state.locks):
        #         state.locks = locks
        #         self.public_repo.set_state(state, transaction)

        #     self.public_repo.set_scoreboard(scoreboard, transaction)

        #     return scoreboard


        # transaction = self.public_repo.firestore.create_transaction()

        scoreboard = update(transaction)

        return ManualUpdateGameResult(command=command, scoreboard=scoreboard)


def create_manual_update_game_command_executor(
    proxy: CoreGameProxy = Depends(create_core_game_proxy),
    public_repo: PublicRepository = Depends(create_public_repository)
):
    return ManualUpdateGameCommandExecutor(
        proxy=proxy,
        public_repo=public_repo
    )
