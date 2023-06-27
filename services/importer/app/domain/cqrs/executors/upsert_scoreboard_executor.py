from fastapi import Depends
from strivelogger import StriveLogger

from app.config.settings import Settings, get_settings
from app.domain.cqrs.command_result import CommandResult

from ...services.scoreboard_service import ScoreboardService, create_scoreboard_service
from ...store.scoreboard_store import ScoreboardStore, create_scoreboard_store
from ..commands.upsert_scoreboard_command import UpsertScoreboardCommand


class UpsertScoreboardExecutor:
    def __init__(self, settings: Settings, service: ScoreboardService, store: ScoreboardStore):
        self.settings = settings
        self.service = service
        self.store = store

    def execute(self, command: UpsertScoreboardCommand) -> CommandResult:
        try:
            scoreboard = self.service.get_scoreboard()
        except Exception as e:
            StriveLogger.error("Failed to load scoreboard", exc_info=e)
            return CommandResult.failure_result("Failed to load scoreboard")

        existing_scoreboard = self.store.get_scoreboard()

        needs_update = existing_scoreboard is None or existing_scoreboard.hash() != scoreboard.hash()

        if not needs_update:
            StriveLogger.info("Scoreboard is up to date")
            return CommandResult.success_result()

        try:
            StriveLogger.info("Saving scoreboard")
            self.store.save_scoreboard(scoreboard)
        except Exception as e:
            StriveLogger.error("Failed to save scoreboard", exc_info=e)
            return CommandResult.failure_result("Failed to save scoreboard")

        StriveLogger.info("Scoreboard saved")
        return CommandResult.success_result()


def create_upsert_scoreboard_executor(
    settings: Settings = Depends(get_settings),
    service: ScoreboardService = Depends(create_scoreboard_service),
    store: ScoreboardStore = Depends(create_scoreboard_store),
) -> UpsertScoreboardExecutor:
    return UpsertScoreboardExecutor(
        settings=settings,
        service=service,
        store=store,
    )
