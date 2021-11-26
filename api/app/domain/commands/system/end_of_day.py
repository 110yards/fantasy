
from api.app.core.date_utils import hours_since
import pytz
from api.app.config.settings import Settings, get_settings
from api.app.core.logging import Logger
from api.app.domain.commands.league.process_waivers import ProcessWaiversCommand
from api.app.domain.enums.league_command_type import LeagueCommandType
from api.app.domain.services.league_command_push_data import LeagueCommandPushData
from api.app.domain.commands.league.calculate_results import CalculateResultsCommand
from pydantic.main import BaseModel
from api.app.domain.topics import END_OF_WAIVERS_TOPIC, END_OF_WEEK_TOPIC, LEAGUE_COMMAND_TOPIC
from typing import Optional
from api.app.core.publisher import Publisher, create_publisher
from api.app.domain.entities.state import Locks, State
from datetime import datetime, timedelta
from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository
from api.app.domain.repositories.state_repository import StateRepository, create_state_repository
from fastapi import Depends
from api.app.core.annotate_args import annotate_args
from api.app.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin.firestore import firestore
from google.cloud.firestore import Transaction


def create_end_of_day_command_executor(
    state_repo: StateRepository = Depends(create_state_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
    publisher: Publisher = Depends(create_publisher),
    settings: Settings = Depends(get_settings),
):
    return EndOfDayCommandExecutor(
        state_repo=state_repo,
        public_repo=public_repo,
        publisher=publisher,
        settings=settings,
    )


@annotate_args
class EndOfDayCommand(BaseCommand):
    pass


@annotate_args
class EndOfDayResult(BaseCommandResult[EndOfDayCommand]):
    state: Optional[State]
    completed_week_number: Optional[int]
    waivers_enabled = False
    waivers_complete = False


class EndOfDayCommandExecutor(BaseCommandExecutor[EndOfDayCommand, EndOfDayResult]):
    def __init__(
        self,
        state_repo: StateRepository,
        public_repo: PublicRepository,
        publisher: Publisher,
        settings: Settings,
    ):
        self.state_repo = state_repo
        self.public_repo = public_repo
        self.publisher = publisher
        self.settings = settings

    def on_execute(self, command: EndOfDayCommand) -> EndOfDayResult:

        @firestore.transactional
        def end_of_day(transaction: Transaction) -> EndOfDayResult:
            scoreboard = self.public_repo.get_scoreboard(transaction)

            state = self.state_repo.get(transaction)

            if not state.waivers_active:
                Logger.info("Waivers not active")
                week_complete = scoreboard.all_games_complete()

                if not week_complete:
                    Logger.info("Week not yet complete")
                    return EndOfDayResult(command=command)

                now = datetime.now(tz=pytz.UTC)
                hours_since_last_game = hours_since(scoreboard.last_game_start_time(), now)
                if hours_since_last_game < self.settings.min_stat_correction_hours:
                    Logger.info("Week complete but not enough time since last game", extra={
                        "hours_since": hours_since_last_game,
                        "min_hours": self.settings.min_stat_correction_hours
                    })
                    return EndOfDayResult(command=command)

                Logger.info("Week is complete, enabling waivers and publishing end of week")
                state.waivers_active = True
                state.waivers_end = datetime.now().today() + timedelta(days=1)
                state.locks = Locks.reset()
                completed_week_number = scoreboard.week()
                state.current_week = completed_week_number + 1

                self.state_repo.set(state, transaction)

                return EndOfDayResult(command=command, state=state, waivers_enabled=True, completed_week_number=completed_week_number)
            else:
                Logger.info("Waivers are active, initializing waiver processing")
                state.waivers_active = False
                state.waivers_end = None
                self.state_repo.set(state, transaction)

                return EndOfDayResult(command=command, state=state, waivers_complete=True)

        transaction = self.state_repo.firestore.create_transaction()
        result: EndOfDayResult = end_of_day(transaction)

        if result.success and result.waivers_enabled:
            self.publisher.publish(BaseModel(), END_OF_WEEK_TOPIC)

            command = CalculateResultsCommand(week_number=result.completed_week_number)
            payload = LeagueCommandPushData(command_type=LeagueCommandType.CALCULATE_RESULTS, command_data=command.dict())
            self.publisher.publish(payload, LEAGUE_COMMAND_TOPIC)

        if result.success and result.waivers_complete:
            self.publisher.publish(BaseModel(), END_OF_WAIVERS_TOPIC)
            command = ProcessWaiversCommand()
            payload = LeagueCommandPushData(command_type=LeagueCommandType.PROCESS_WAIVERS, command_data=command.dict())
            self.publisher.publish(payload, LEAGUE_COMMAND_TOPIC)

        return result
