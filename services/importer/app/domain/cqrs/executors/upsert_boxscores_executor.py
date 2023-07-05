from datetime import datetime

from fastapi import Depends
from strivelogger import StriveLogger

from app.domain.cqrs.command_result import CommandResult
from app.domain.cqrs.commands.upsert_boxscores_command import (
    UpsertBoxscoresCommand,
)
from app.domain.store.boxscore_store import BoxscoreStore, create_boxscore_store

from ...models.boxscore import Boxscore


class UpsertBoxscoresExecutor:
    def __init__(self, store: BoxscoreStore):
        self.store = store

    def execute(self, command: UpsertBoxscoresCommand) -> CommandResult:
        if len(command.boxscores) == 0:
            StriveLogger.info("No boxscores")
            return CommandResult.success()

        to_update: list[Boxscore] = []

        for box in command.boxscores:
            existing_game = self.store.get_boxscore(datetime.now().year, box.game_id)
            if existing_game is None or existing_game.hash() != box.hash():
                to_update.append(box)

        if not to_update:
            StriveLogger.info("No boxscores have changed")
            return CommandResult.success_result()

        try:
            StriveLogger.info(f"Saving {len(to_update)} boxscores")
            for box in to_update:
                self.store.save_boxscore(datetime.now().year, box)
        except Exception as e:
            StriveLogger.error("Failed to save boxscores(s)", exc_info=e)
            return CommandResult.failure_result("Failed to save boxscores(s)")

        StriveLogger.info("Boxscores saved")
        return CommandResult.success_result()


def create_upsert_boxscores_executor(
    store: BoxscoreStore = Depends(create_boxscore_store),
) -> UpsertBoxscoresExecutor:
    return UpsertBoxscoresExecutor(
        store=store,
    )
