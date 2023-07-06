from datetime import datetime

import pytz
from fastapi import Depends
from pydantic.main import BaseModel
from strivelogger import StriveLogger

from app.config.settings import Settings, get_settings
from app.di import create_publisher
from app.domain.services.end_of_week_service import EndOfWeekRequest
from app.domain.services.league_command_push_data import LeagueCommandPushData

from ...core.date_utils import hours_since
from ...core.publisher import Publisher
from ...core.pubsub.topics import END_OF_WEEK_TOPIC
from ..cqrs.command_result import CommandResult
from ..cqrs.commands.system.start_system_waivers_command import StartSystemWaiversCommand
from ..cqrs.executors.system.start_system_waivers_executor import StartSystemWaiversExecutor
from ..store.scoreboard_store import ScoreboardStore
from ..store.state_store import StateStore


class EndOfDayWorkflow:
    def __init__(
        self,
        publisher: Publisher,
        settings: Settings,
        state_store: StateStore,
        scoreboard_store: ScoreboardStore,
        start_system_waivers_executor: StartSystemWaiversExecutor,
        end_system_waivers_command_executor: EndSystemWaiversCommandExecutor,
    ):
        self.publisher = publisher
        self.settings = settings
        self.state_store = state_store
        self.scoreboard_store = scoreboard_store
        self.start_system_waivers_executor = start_system_waivers_executor
        self.end_system_waivers_command_executor = end_system_waivers_command_executor

    def run_workflow(self) -> CommandResult:
        StriveLogger.info("End of day workflow started")
        state = self.state_store.get()

        if not state.waivers_active and self.should_start_waivers():
            return self.start_waivers(state.current_week)

        elif state.waivers_active:
            self.end_waivers()

        StriveLogger.info("End of day workflow completed")

    def should_start_waivers(self) -> bool:
        scoreboard = self.scoreboard_store.get_scoreboard()
        week_complete = scoreboard.all_games_complete()

        if not week_complete:
            StriveLogger.info("Week not yet complete")
            return False

        now = datetime.now(tz=pytz.UTC)
        hours_since_last_game = hours_since(scoreboard.last_game_start_time(), now)
        if hours_since_last_game < self.settings.min_stat_correction_hours:
            StriveLogger.info(
                "Week complete but not enough time since last game",
                extra={"hours_since": hours_since_last_game, "min_hours": self.settings.min_stat_correction_hours},
            )
            return False

        return True

    def start_waivers(self, current_week: int) -> CommandResult:
        StriveLogger.info("Week is complete, enabling waivers and publishing end of week")
        command = StartSystemWaiversCommand(current_week_number=current_week)
        result = self.start_system_waivers_executor.execute(command)

        if result.success:
            # triggers the system to recalculate player season stats
            self.publisher.publish(EndOfWeekRequest(completed_week_number=result.completed_week_number), END_OF_WEEK_TOPIC)

            # triggers leagues to calculate weekly results
            command = CalculateResultsCommand(week_number=result.completed_week_number)
            payload = LeagueCommandPushData(command_type=LeagueCommandType.CALCULATE_RESULTS, command_data=command.dict())
            self.publisher.publish(payload, LEAGUE_COMMAND_TOPIC)

        return result

    def end_waivers(self):
        StriveLogger.info("Waivers are active, initializing waiver processing")
        command = EndSystemWaiversCommand()
        result = self.end_system_waivers_command_executor.execute(command)

        if result.success:
            # Future proofing
            self.publisher.publish(BaseModel(), END_OF_WAIVERS_TOPIC)

            # triggers leagues to process waivers
            command = ProcessWaiversCommand()
            payload = LeagueCommandPushData(command_type=LeagueCommandType.PROCESS_WAIVERS, command_data=command.dict())
            self.publisher.publish(payload, LEAGUE_COMMAND_TOPIC)


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
        start_system_waivers_executor=start_system_waivers_command_executor,
        end_system_waivers_command_executor=end_system_waivers_command_executor,
        settings=settings,
    )
