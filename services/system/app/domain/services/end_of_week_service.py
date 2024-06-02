
from ..commands.system.update_schedule import UpdateScheduleCommand, UpdateScheduleCommandExecutor
from yards_py.core.publisher import Publisher
from services.system.app.di import create_publisher
from services.system.app.domain.commands.league.calculate_season_score import CalculateSeasonScoreCommand
from services.system.app.domain.commands.system.recalc_season_stats import (
    RecalcSeasonStatsCommand, RecalcSeasonStatsCommandExecutor, create_recalc_season_stats_command_executor)
from fastapi import Depends
from pydantic.main import BaseModel

from yards_py.domain.enums.league_command_type import LeagueCommandType
from services.system.app.domain.services.league_command_push_data import LeagueCommandPushData
from yards_py.domain.topics import LEAGUE_COMMAND_TOPIC


class EndOfWeekRequest(BaseModel):
    completed_week_number: int


class EndOfWeekService:
    def __init__(
        self,
        publisher: Publisher,
        update_schedule_command_executor: UpdateScheduleCommandExecutor,
        recalc_season_stats_command_executor: RecalcSeasonStatsCommandExecutor
    ):
        self.publisher = publisher
        self.update_schedule_command_executor = update_schedule_command_executor
        self.recalc_season_stats_command_executor = recalc_season_stats_command_executor

    def run_workflow(self, completed_week_number) -> bool:
        # update the schedule; this will also update the scoreboard, opponents and locks
        update_schedule_command = UpdateScheduleCommand()
        result = self.update_schedule_command_executor.execute(update_schedule_command)

        if not result.success:
            raise Exception("Failed to update schedule")

        # recalculate the season stats
        recalc_command = RecalcSeasonStatsCommand(completed_week_number=completed_week_number)
        result = self.recalc_season_stats_command_executor.execute(recalc_command)

        # if successful, tell leagues to calculate the season score
        if result.success:
            command = CalculateSeasonScoreCommand()
            payload = LeagueCommandPushData(command_type=LeagueCommandType.CALCULATE_SEASON_SCORE, command_data=command.dict())
            self.publisher.publish(payload, LEAGUE_COMMAND_TOPIC)

        return result.success


def create_end_of_week_service(
    publisher: Publisher = Depends(create_publisher),
    recalc_season_stats_command_executor: RecalcSeasonStatsCommandExecutor = Depends(create_recalc_season_stats_command_executor)
):
    return EndOfWeekService(publisher, recalc_season_stats_command_executor)

