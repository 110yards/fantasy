from datetime import datetime, timezone

from dictdiffer import diff
from fastapi import Depends
from strivelogger import StriveLogger

from app.domain.cqrs.command_result import CommandResult
from app.domain.cqrs.commands.upsert_boxscores_command import (
    UpsertBoxscoresCommand,
)
from app.domain.store.boxscore_store import BoxscoreStore, create_boxscore_store

from ....core.publisher import Publisher, create_publisher
from ....core.pubsub.topics import BOXSCORES_UPDATED_TOPIC
from ...models.boxscore import Boxscore


class UpsertBoxscoresExecutor:
    def __init__(self, store: BoxscoreStore, publisher: Publisher):
        self.store = store
        self.publisher = publisher

    def execute(self, command: UpsertBoxscoresCommand) -> CommandResult:
        if len(command.boxscores) == 0:
            StriveLogger.info("No boxscores")
            return CommandResult.success_result()

        to_update: list[Boxscore] = []

        for box in command.boxscores:
            existing_game = self.store.get_boxscore(datetime.now().year, box.game_id)

            if existing_game and existing_game.source == "official" and box.source == "realtime":
                continue  # don't overwrite official boxscores with realtime boxscores

            has_diffs = (
                existing_game is None or len(list(diff(existing_game.model_dump(exclude={"last_updated"}), box.model_dump(exclude={"last_updated"})))) > 0
            )
            if has_diffs:
                box.last_updated = datetime.now(tz=timezone.utc)
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

        self.publisher.publish(BOXSCORES_UPDATED_TOPIC)
        StriveLogger.info(f"Published {BOXSCORES_UPDATED_TOPIC}")

        return CommandResult.success_result()


def create_upsert_boxscores_executor(
    store: BoxscoreStore = Depends(create_boxscore_store),
    publisher: Publisher = Depends(create_publisher),
) -> UpsertBoxscoresExecutor:
    return UpsertBoxscoresExecutor(
        store=store,
        publisher=publisher,
    )
