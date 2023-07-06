

from app.yards_py.core.publisher import Publisher, create_publisher
from app.domain.commands.league.calculate_season_score import CalculateSeasonScoreCommand
from app.domain.commands.system.recalc_season_stats import (
    RecalcSeasonStatsCommand, RecalcSeasonStatsCommandExecutor, create_recalc_season_stats_command_executor)
from fastapi import Depends
from pydantic.main import BaseModel

from app.yards_py.domain.enums.league_command_type import LeagueCommandType
from app.domain.services.league_command_push_data import LeagueCommandPushData
from app.yards_py.domain.topics import LEAGUE_COMMAND_TOPIC


def create_end_of_week_service(
    publisher: Publisher = Depends(create_publisher),
    recalc_season_stats_command_executor: RecalcSeasonStatsCommandExecutor = Depends(create_recalc_season_stats_command_executor)
):
    return EndOfWeekService(publisher, recalc_season_stats_command_executor)


class EndOfWeekRequest(BaseModel):
    completed_week_number: int


class EndOfWeekService:
    def __init__(
        self,
        publisher: Publisher,
        recalc_season_stats_command_executor: RecalcSeasonStatsCommandExecutor
    ):
        self.publisher = publisher
        self.recalc_season_stats_command_executor = recalc_season_stats_command_executor

    def run_workflow(self, completed_week_number) -> bool:
        # This is wrapped in a service for clarity and future flexibility, even though it only has one step currently.
        recalc_command = RecalcSeasonStatsCommand(completed_week_number=completed_week_number)

        result = self.recalc_season_stats_command_executor.execute(recalc_command)

        if result.success:
            command = CalculateSeasonScoreCommand()
            payload = LeagueCommandPushData(command_type=LeagueCommandType.CALCULATE_SEASON_SCORE, command_data=command.dict())
            self.publisher.publish(payload, LEAGUE_COMMAND_TOPIC)

        return result.success
