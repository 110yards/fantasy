from __future__ import annotations

from yards_py.domain.entities.opponents import Opponents
from yards_py.domain.entities.scoreboard import Scoreboard
from yards_py.domain.entities.season_schedule import SeasonSchedule
from yards_py.domain.entities.state import Locks
from ....api_proxies.core.core_schedule_proxy import CoreScheduleProxy, create_core_schedule_proxy


from yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository
from yards_py.core.logging import Logger

import logging

from yards_py.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult

from fastapi.param_functions import Depends
from timeit import default_timer as timer

from firebase_admin import firestore

logger = logging.getLogger()



"""
Not sure if this will persist past 2024, right now it pulls the schedule and adds it to the state, that should happen on import.  Maybe this should happen periodically as well?
"""
class UpdateScheduleCommand(BaseCommand):
    season: int | None = None


class UpdateScheduleResult(BaseCommandResult):
    schedule: SeasonSchedule


class UpdateScheduleCommandExecutor(BaseCommandExecutor[UpdateScheduleCommand, UpdateScheduleResult]):

    def __init__(
        self,
        proxy: CoreScheduleProxy,
        public_repo: PublicRepository,
    ):
        self.proxy = proxy
        self.public_repo = public_repo

    def on_execute(self, command: UpdateScheduleCommand) -> UpdateScheduleResult:
        start = timer()

        Logger.info("Updating schedule")

        Logger.debug(f"Loading schedule ({timer() - start})")
        schedule_data = self.proxy.get_schedule(command.season)
        schedule = SeasonSchedule(**schedule_data)

        @firestore.transactional
        def update(transaction) -> SeasonSchedule:
            state = self.public_repo.get_state(transaction)

            games = [game for game in schedule.games if game.week == state.current_week]

            scoreboard = Scoreboard.create(games)
            opponents = Opponents.from_scheduled_games(games)
            state.locks = Locks.create_from_scoreboard(scoreboard)


            self.public_repo.set_schedule(schedule, transaction)
            self.public_repo.set_scoreboard(scoreboard, transaction)
            self.public_repo.set_opponents(opponents, transaction)                      

            self.public_repo.set_state(state, transaction)

            return schedule
        
        transaction = self.public_repo.firestore.create_transaction()
        schedule = update(transaction)

        Logger.debug(f"Schedule updated ({timer() - start})")

        return UpdateScheduleResult(command=command, schedule=schedule)


def create_update_schedule_command_executor(    
    proxy: CoreScheduleProxy = Depends(create_core_schedule_proxy),
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return UpdateScheduleCommandExecutor(
        proxy=proxy,
        public_repo=public_repo,
    )
