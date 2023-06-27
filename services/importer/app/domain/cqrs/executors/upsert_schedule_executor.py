from datetime import datetime

from fastapi import Depends
from strivelogger import StriveLogger

from app.config.settings import Settings, get_settings
from app.domain.cqrs.command_result import CommandResult
from app.domain.cqrs.commands.upsert_schedule_command import UpsertScheduleCommand
from app.domain.services.schedule_service import (
    ScheduleService,
    create_schedule_service,
)
from app.domain.store.schedule_store import ScheduleStore, create_schedule_store


class UpsertScheduleExecutor:
    def __init__(self, settings: Settings, service: ScheduleService, store: ScheduleStore):
        self.settings = settings
        self.service = service
        self.store = store

    def execute(self, command: UpsertScheduleCommand) -> CommandResult:
        try:
            schedule = self.service.get_schedule()
        except Exception as e:
            StriveLogger.error("Failed to load schedule", exc_info=e)
            return CommandResult.failure_result("Failed to load schedule")

        if schedule.year != datetime.now().year:
            StriveLogger.warn("Schedule is not for the current year")
            return CommandResult.failure_result("Schedule is not for the current year")

        existing_schedule = self.store.get_schedule(schedule.year)

        needs_update = existing_schedule is None or existing_schedule.hash() != schedule.hash()

        if not needs_update:
            StriveLogger.info("Schedule is up to date")
            return CommandResult.success_result()

        try:
            StriveLogger.info("Saving schedule")
            self.store.save_schedule(schedule)
        except Exception as e:
            StriveLogger.error("Failed to save schedule", exc_info=e)
            return CommandResult.failure_result("Failed to save schedule")

        StriveLogger.info("Schedule saved")
        return CommandResult.success_result()


def create_upsert_schedule_executor(
    settings: Settings = Depends(get_settings),
    service: ScheduleService = Depends(create_schedule_service),
    store: ScheduleStore = Depends(create_schedule_store),
) -> UpsertScheduleExecutor:
    return UpsertScheduleExecutor(
        settings=settings,
        service=service,
        store=store,
    )
