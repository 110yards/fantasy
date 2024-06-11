from __future__ import annotations


from ....api_proxies.core.core_scoreboard_proxy import CoreScoreboardProxy, create_core_scoreboard_proxy
from yards_py.domain.entities.scoreboard import Scoreboard, ScoreboardGame
from yards_py.domain.entities.state import Locks
from yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository

import logging

from yards_py.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult

from fastapi.param_functions import Depends

from firebase_admin import firestore

from yards_py.core.logging import Logger



class ManualUpdateScoreboardCommand(BaseCommand):
    pass


class ManualUpdateScoreboardResult(BaseCommandResult):
    scoreboard: Scoreboard | None


class ManualUpdateScoreboardCommandExecutor(BaseCommandExecutor[ManualUpdateScoreboardCommand, ManualUpdateScoreboardResult]):
    def __init__(
        self,
        proxy: CoreScoreboardProxy,
        public_repo: PublicRepository,
    ):
        self.proxy = proxy
        self.public_repo = public_repo

    def on_execute(self, command: ManualUpdateScoreboardCommand) -> ManualUpdateScoreboardResult:
        @firestore.transactional
        def update(transaction) -> Scoreboard | None:
            state = self.public_repo.get_state(transaction)

            data = self.proxy.get_scoreboard(state.current_season, state.current_week)

            games = [ScoreboardGame(**x) for x in data["games"]]
            games = {x.game_id: x for x in games}
            scoreboard = Scoreboard(games=games)            

            locks = Locks.create_from_scoreboard(scoreboard)

            if locks.changed(state.locks):
                state.locks = locks
                self.public_repo.set_state(state, transaction)

            self.public_repo.set_scoreboard(scoreboard, transaction)

            return scoreboard


        transaction = self.public_repo.firestore.create_transaction()

        scoreboard = update(transaction)

        return ManualUpdateScoreboardResult(command=command, scoreboard=scoreboard)


def create_manual_update_scoreboard_command_executor(
    proxy: CoreScoreboardProxy = Depends(create_core_scoreboard_proxy),
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return ManualUpdateScoreboardCommandExecutor(
        proxy=proxy,
        public_repo=public_repo
    )
