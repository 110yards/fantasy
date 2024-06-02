from __future__ import annotations


from yards_py.domain.entities.scoreboard import Scoreboard, ScoreboardGame
from yards_py.domain.entities.state import Locks
from yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository

import logging

from yards_py.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult

from fastapi.param_functions import Depends

from firebase_admin import firestore

from yards_py.core.logging import Logger



class UpdateScoreboardCommand(BaseCommand):
    scoreboard_game: ScoreboardGame


class UpdateScoreboardResult(BaseCommandResult):
    scoreboard: Scoreboard | None


class UpdateScoreboardCommandExecutor(BaseCommandExecutor[UpdateScoreboardCommand, UpdateScoreboardResult]):
    def __init__(
        self,
        public_repo: PublicRepository,
    ):
        self.public_repo = public_repo

    def on_execute(self, command: UpdateScoreboardCommand) -> UpdateScoreboardResult:
        @firestore.transactional
        def update(transaction) -> Scoreboard | None:
            state = self.public_repo.get_state(transaction)

            # is this game for this year and week?
            if command.scoreboard_game.year != state.current_season or command.scoreboard_game.week != state.current_week:
                Logger.info(f"Game is not for current season/week: {command.scoreboard_game.year}/{command.scoreboard_game.week}, scoreboard will not be updated")
                return None


            scoreboard = self.public_repo.get_scoreboard(transaction)

            scoreboard.games[command.scoreboard_game.game_id] = command.scoreboard_game

            locks = Locks.create_from_scoreboard(scoreboard)

            if locks.changed(state.locks):
                state.locks = locks
                self.public_repo.set_state(state, transaction)

            self.public_repo.set_scoreboard(scoreboard, transaction)

            return scoreboard


        transaction = self.public_repo.firestore.create_transaction()

        scoreboard = update(transaction)

        return UpdateScoreboardResult(command=command, scoreboard=scoreboard)


def create_update_scoreboard_command_executor(
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return UpdateScoreboardCommandExecutor(public_repo=public_repo)
