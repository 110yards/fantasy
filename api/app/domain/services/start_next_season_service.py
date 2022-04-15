from typing import Any, Optional
from api.app.core.logging import Logger

from api.app.domain.commands.system.update_schedule import UpdateScheduleCommand, UpdateScheduleCommandExecutor, create_update_schedule_command_executor
from api.app.domain.entities.event_type import EVENT_TYPE_REGULAR
from api.app.domain.entities.opponents import Opponents
from api.app.domain.entities.scoreboard import Scoreboard
from api.app.domain.entities.state import Locks, State
from api.app.domain.repositories.public_repository import (
    PublicRepository, create_public_repository)

from fastapi import Depends
from pydantic.main import BaseModel


def create_start_next_season_service(
    update_schedule_command_executor: UpdateScheduleCommandExecutor = Depends(create_update_schedule_command_executor),
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return StartNextSeasonService(
        update_schedule_command_executor=update_schedule_command_executor,
        public_repo=public_repo,
    )


class StartNextSeasonResult(BaseModel):
    success: bool
    error: Optional[str]
    state: Optional[State]
    scoreboard: Optional[Scoreboard]
    opponents: Optional[Opponents]


class StartNextSeasonService:
    def __init__(
        self,
        update_schedule_command_executor: UpdateScheduleCommandExecutor,
        public_repo: PublicRepository,
    ):
        self.update_schedule_command_executor = update_schedule_command_executor
        self.public_repo = public_repo

    def run_workflow(self) -> Any:
        Logger.info("Start next season workflow started")

        # update season / week (state)
        state = self.public_repo.get_state()
        state.current_season += 1
        state.current_week = 1
        state.season_weeks = 21
        state.locks = Locks.create(all_games_active=False)
        state.is_offseason = False
        state.waivers_end = None
        state.waivers_active = False

        # update schedule
        # not strictly necessary to include final, but maybe helpful for testing with old seasons
        command = UpdateScheduleCommand(include_final=True, season=state.current_season)
        schedule_result = self.update_schedule_command_executor.execute(command)

        if not schedule_result.success:
            return StartNextSeasonResult(success=False, error=schedule_result.error)

        # update scoreboard
        week_one_games = [game for game in schedule_result.games if game.week == 1 and game.event_type.event_type_id == EVENT_TYPE_REGULAR]
        scoreboard = Scoreboard.create(week_one_games)  # kinda sketchy, relies on ScheduledGame being similar enough to Game

        # update opponents
        opponents = Opponents.from_scheduled_games(week_one_games)

        # save state new state
        self.public_repo.set_state(state)
        self.public_repo.set_scoreboard(scoreboard)
        self.public_repo.set_opponents(opponents)

        return StartNextSeasonResult(
            success=True,
            state=state,
            scoreboard=scoreboard,
            opponents=opponents
        )
