# TODO: REMOVE THIS

from api.app.domain.commands.league.calculate_playoffs import (
    CalculatePlayoffsCommand, CalculatePlayoffsCommandExecutor,
    create_calculate_playoffs_command_executor)
from api.app.domain.commands.league.calculate_results import (
    CalculateResultsCommand, CalculateResultsCommandExecutor,
    create_calculate_results_command_executor)
from api.app.domain.commands.league.calculate_season_score import (
    CalculateSeasonScoreCommand, CalculateSeasonScoreCommandExecutor,
    create_calculate_season_score_command_executor)
from api.app.domain.commands.league.process_waivers import (
    ProcessWaiversCommand, ProcessWaiversCommandExecutor,
    create_process_waivers_command_executor)
from api.app.domain.commands.system.end_system_waivers import \
    EndSystemWaiversResult
from api.app.domain.commands.system.start_system_waivers import \
    StartSystemWaiversResult
from api.app.domain.repositories.league_repository import (
    LeagueRepository, create_league_repository)
from api.app.domain.services.end_of_day_service import (
    EndOfDayService, create_end_of_day_service)
from api.app.domain.services.end_of_week_service import (
    EndOfWeekService, create_end_of_week_service)
from fastapi.param_functions import Depends


def create_simulate_end_of_day(
    end_of_day_service: EndOfDayService = Depends(create_end_of_day_service),
    end_of_week_service: EndOfWeekService = Depends(create_end_of_week_service),
    league_repo: LeagueRepository = Depends(create_league_repository),
    calculate_results_command_executor: CalculateResultsCommandExecutor = Depends(create_calculate_results_command_executor),
    process_waivers_command_executor: ProcessWaiversCommandExecutor = Depends(create_process_waivers_command_executor),
    calculate_playoffs_command_executor: CalculatePlayoffsCommandExecutor = Depends(create_calculate_playoffs_command_executor),
    calculate_season_score_command_executor: CalculateSeasonScoreCommandExecutor = Depends(create_calculate_season_score_command_executor),
):
    return SimulateEndOfDay(
        end_of_day_service,
        end_of_week_service,
        league_repo,
        calculate_results_command_executor,
        process_waivers_command_executor,
        calculate_playoffs_command_executor,
        calculate_season_score_command_executor,
    )


class SimulateEndOfDay:
    def __init__(
        self,
        end_of_day_service: EndOfDayService,
        end_of_week_service: EndOfWeekService,
        league_repo: LeagueRepository,
        calculate_results_command_executor: CalculateResultsCommandExecutor,
        process_waivers_command_executor: ProcessWaiversCommandExecutor,
        calculate_playoffs_command_executor: CalculatePlayoffsCommandExecutor,
        calculate_season_score_command_executor: CalculateSeasonScoreCommandExecutor,
    ):
        self.end_of_day_service = end_of_day_service
        self.end_of_week_service = end_of_week_service
        self.league_repo = league_repo
        self.calculate_results_command_executor = calculate_results_command_executor
        self.process_waivers_command_executor = process_waivers_command_executor
        self.calculate_playoffs_command_executor = calculate_playoffs_command_executor
        self.calculate_season_score_command_executor = calculate_season_score_command_executor

    def run(self):
        result = self.end_of_day_service.run_workflow()

        if isinstance(result, StartSystemWaiversResult) and result.success:
            week_number = result.completed_week_number
            success = self.end_of_week_service.run_workflow(week_number)

            if success:
                self.__calculate_league_results(week_number)

        if isinstance(result, EndSystemWaiversResult) and result.success:
            leagues = self.league_repo.get_all()
            for league in leagues:
                command = ProcessWaiversCommand(league_id=league.id)
                self.process_waivers_command_executor.execute(command)

    def __calculate_league_results(self, week_number):
        leagues = self.league_repo.get_all()

        for league in leagues:
            scores_command = CalculateSeasonScoreCommand(league_id=league.id)
            self.calculate_season_score_command_executor.execute(scores_command)

            results_command = CalculateResultsCommand(league_id=league.id, week_number=week_number)
            calc_result = self.calculate_results_command_executor.execute(results_command)

            if calc_result.success and calc_result.next_week_is_playoffs:
                results_command = CalculatePlayoffsCommand(league.id, week_number + 1)
                self.calculate_playoffs_command_executor.execute(results_command)
