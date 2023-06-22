from fastapi import Depends
from strivelogger import StriveLogger

from app.config.settings import Settings, get_settings
from app.domain.cqrs.command_result import CommandResult
from app.domain.cqrs.commands.upsert_schedule_command import UpsertScheduleCommand
from app.domain.services.injury_report_service import (
    InjuryReportService,
    create_injury_report_service,
)
from app.domain.store.injury_report_store import (
    InjuryReportStore,
    create_injury_report_store,
)


class UpsertInjuryReportExecutor:
    def __init__(self, settings: Settings, service: InjuryReportService, store: InjuryReportStore):
        self.settings = settings
        self.service = service
        self.store = store

    def execute(self, command: UpsertScheduleCommand) -> CommandResult:
        try:
            report = self.service.get_report()
        except Exception as e:
            StriveLogger.error("Failed to load schedule", exc_info=e)
            return CommandResult.failure("Failed to load schedule")

        existing = self.store.get_report()
        needs_update = existing is None or existing.hash() != report.hash()

        if not needs_update:
            StriveLogger.info("Injury report is up to date")
            return CommandResult.success()

        try:
            StriveLogger.info("Saving injury report")
            self.store.save_report(report)
        except Exception as e:
            StriveLogger.error("Failed to save report", exc_info=e)
            return CommandResult.failure("Failed to save report")

        StriveLogger.info("Injury report saved")
        return CommandResult.success()


def create_upsert_injury_report_executor(
    settings: Settings = Depends(get_settings),
    service: InjuryReportService = Depends(create_injury_report_service),
    store: InjuryReportStore = Depends(create_injury_report_store),
) -> UpsertInjuryReportExecutor:
    return UpsertInjuryReportExecutor(
        settings=settings,
        service=service,
        store=store,
    )
