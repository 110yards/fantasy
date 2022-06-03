from datetime import datetime
from yards_py.core.base_command_executor import BaseCommandResult
from yards_py.core.logging import Logger

import pytz
from services.system.app.config.settings import Settings, get_settings
from yards_py.core.date_utils import hours_since
from yards_py.core.publisher import Publisher
from services.system.app.di import create_publisher
from services.system.app.domain.commands.league.calculate_results import \
    CalculateResultsCommand
from services.system.app.domain.commands.league.process_waivers import \
    ProcessWaiversCommand
from services.system.app.domain.commands.system.end_system_waivers import (
    EndSystemWaiversCommand, EndSystemWaiversCommandExecutor,
    create_end_system_waivers_command_executor)
from services.system.app.domain.commands.system.start_system_waivers import (
    StartSystemWaiversCommand, StartSystemWaiversCommandExecutor, StartSystemWaiversResult,
    create_start_system_waivers_command_executor)
from yards_py.domain.enums.league_command_type import LeagueCommandType
from yards_py.domain.repositories.public_repository import (
    PublicRepository, create_public_repository)
from services.system.app.domain.services.end_of_week_service import EndOfWeekRequest
from services.system.app.domain.services.league_command_push_data import \
    LeagueCommandPushData
from yards_py.domain.topics import (END_OF_WAIVERS_TOPIC, END_OF_WEEK_TOPIC,
                                    LEAGUE_COMMAND_TOPIC)
from fastapi import Depends
from pydantic.main import BaseModel


def create_end_of_day_service(
    publisher: Publisher = Depends(create_publisher),
    public_repo: PublicRepository = Depends(create_public_repository),
    start_system_waivers_command_executor: StartSystemWaiversCommandExecutor = Depends(create_start_system_waivers_command_executor),
    end_system_waivers_command_executor: EndSystemWaiversCommandExecutor = Depends(create_end_system_waivers_command_executor),
    settings: Settings = Depends(get_settings),

):
    return EndOfDayService(
        publisher=publisher,
        public_repo=public_repo,
        start_system_waivers_command_executor=start_system_waivers_command_executor,
        end_system_waivers_command_executor=end_system_waivers_command_executor,
        settings=settings,
    )


class EndOfDayService:
    def __init__(
        self,
        publisher: Publisher,
        settings: Settings,
        public_repo: PublicRepository,
        start_system_waivers_command_executor: StartSystemWaiversCommandExecutor,
        end_system_waivers_command_executor: EndSystemWaiversCommandExecutor,
    ):
        self.publisher = publisher
        self.settings = settings
        self.public_repo = public_repo
        self.start_system_waivers_command_executor = start_system_waivers_command_executor
        self.end_system_waivers_command_executor = end_system_waivers_command_executor

    def run_workflow(self) -> BaseCommandResult:
        Logger.info("End of day workflow started")
        state = self.public_repo.get_state()

        if not state.waivers_active and self.should_start_waivers():
            return self.start_waivers(state.current_week)

        elif state.waivers_active:
            self.end_waivers()

        Logger.info("End of day workflow completed")

    def should_start_waivers(self) -> bool:
        # TODO: write a test for this
        scoreboard = self.public_repo.get_scoreboard()
        week_complete = scoreboard.all_games_complete()

        if not week_complete:
            Logger.info("Week not yet complete")
            return False

        now = datetime.now(tz=pytz.UTC)
        hours_since_last_game = hours_since(scoreboard.last_game_start_time(), now)
        if hours_since_last_game < self.settings.min_stat_correction_hours:
            Logger.info("Week complete but not enough time since last game", extra={
                "hours_since": hours_since_last_game,
                "min_hours": self.settings.min_stat_correction_hours
            })
            return False

        return True

    def start_waivers(self, current_week: int) -> StartSystemWaiversResult:
        Logger.info("Week is complete, enabling waivers and publishing end of week")
        command = StartSystemWaiversCommand(current_week_number=current_week)
        result = self.start_system_waivers_command_executor.execute(command)

        if result.success:
            # triggers the system to recalculate player season stats
            self.publisher.publish(EndOfWeekRequest(completed_week_number=result.completed_week_number), END_OF_WEEK_TOPIC)

            # triggers leagues to calculate weekly results
            command = CalculateResultsCommand(week_number=result.completed_week_number)
            payload = LeagueCommandPushData(command_type=LeagueCommandType.CALCULATE_RESULTS, command_data=command.dict())
            self.publisher.publish(payload, LEAGUE_COMMAND_TOPIC)

        return result

    def end_waivers(self):
        Logger.info("Waivers are active, initializing waiver processing")
        command = EndSystemWaiversCommand()
        result = self.end_system_waivers_command_executor.execute(command)

        if result.success:
            # Future proofing
            self.publisher.publish(BaseModel(), END_OF_WAIVERS_TOPIC)

            # triggers leagues to process waivers
            command = ProcessWaiversCommand()
            payload = LeagueCommandPushData(command_type=LeagueCommandType.PROCESS_WAIVERS, command_data=command.dict())
            self.publisher.publish(payload, LEAGUE_COMMAND_TOPIC)
