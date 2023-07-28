from typing import Tuple

from app.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from app.core.pubsub.pubsub_push import PubSubPush
from app.domain.commands.league.calculate_playoffs import CalculatePlayoffsCommand, CalculatePlayoffsCommandExecutor, create_calculate_playoffs_command_executor
from app.domain.commands.league.calculate_results import CalculateResultsCommand, CalculateResultsCommandExecutor, create_calculate_results_command_executor
from app.domain.commands.league.calculate_season_score import (
    CalculateSeasonScoreCommand,
    CalculateSeasonScoreCommandExecutor,
    create_calculate_season_score_command_executor,
)
from app.domain.commands.league.process_waivers import ProcessWaiversCommand, ProcessWaiversCommandExecutor, create_process_waivers_command_executor

# from app.domain.commands.league.update_league_player_details import (
#     UpdateLeaguePlayerDetailsCommand, UpdateLeaguePlayerDetailsCommandExecutor,
#     create_update_league_player_details_command_executor)
from app.domain.enums.league_command_type import LeagueCommandType
from app.domain.services.league_command_push_data import LeagueCommandPushData
from fastapi import Depends


def create_league_command_service(
    # update_league_player_details_cmd_ex: UpdateLeaguePlayerDetailsCommandExecutor = Depends(create_update_league_player_details_command_executor),
    calculate_results_cmd_ex: CalculateResultsCommandExecutor = Depends(create_calculate_results_command_executor),
    calculate_season_score_cmd_ex: CalculateSeasonScoreCommandExecutor = Depends(create_calculate_season_score_command_executor),
    process_waivers_cmd_ex: ProcessWaiversCommandExecutor = Depends(create_process_waivers_command_executor),
    calculate_playoffs_cmd_ex: CalculatePlayoffsCommandExecutor = Depends(create_calculate_playoffs_command_executor),
):
    return LeagueCommandService(
        # update_league_player_details_cmd_ex,
        calculate_results_cmd_ex,
        calculate_season_score_cmd_ex,
        process_waivers_cmd_ex,
        calculate_playoffs_cmd_ex,
    )


class LeagueCommandService:
    def __init__(
        self,
        # update_league_player_details_cmd_ex: UpdateLeaguePlayerDetailsCommandExecutor,
        calculate_results_cmd_ex: CalculateResultsCommandExecutor,
        calculate_season_score_cmd_ex: CalculateSeasonScoreCommandExecutor,
        process_waivers_cmd_ex: ProcessWaiversCommandExecutor,
        calculate_playoffs_cmd_ex: CalculatePlayoffsCommandExecutor,
    ):
        # self.update_league_player_details_cmd_ex = update_league_player_details_cmd_ex
        self.calculate_results_cmd_ex = calculate_results_cmd_ex
        self.calculate_season_score_cmd_ex = calculate_season_score_cmd_ex
        self.process_waivers_cmd_ex = process_waivers_cmd_ex
        self.calculate_playoffs_cmd_ex = calculate_playoffs_cmd_ex

    def execute_league_command(self, league_id: str, push: PubSubPush) -> BaseCommandResult:
        push_data = LeagueCommandPushData(**push.get_data())

        command, executor = self.setup(league_id, push_data)

        if not command:
            return  # do nothing, ack the pub/sub push

        return executor.execute(command)

    def setup(self, league_id: str, push_data: LeagueCommandPushData) -> Tuple[BaseCommand, BaseCommandExecutor]:
        command = None
        executor = None

        # this is a hack, caused by the race condition bug which showed up when I added the calculate_playoffs league command
        # calculate_results_command will send a league command to calculate playoffs at the end of calculating league results,
        # but the results are calculated per league, which results in a league command for calculate playoffs being forwarded
        # to every league subscription.
        # For 2022, this whole piece needs to be refactored as workflows, but for now, ignore any league command
        # which already contains a league ID if that league ID doesn't match the subscription league id.

        command_league_id = push_data.command_data.get("league_id", None)
        if command_league_id is not None and command_league_id != league_id:  # for another league, skip
            return None, None

        push_data.command_data["league_id"] = league_id

        # if push_data.command_type == LeagueCommandType.UPDATE_PLAYER:
        #     command = UpdateLeaguePlayerDetailsCommand(**push_data.command_data)
        #     executor = self.update_league_player_details_cmd_ex

        if push_data.command_type == LeagueCommandType.CALCULATE_RESULTS:
            command = CalculateResultsCommand(**push_data.command_data)
            executor = self.calculate_results_cmd_ex

        if push_data.command_type == LeagueCommandType.CALCULATE_SEASON_SCORE:
            command = CalculateSeasonScoreCommand(**push_data.command_data)
            executor = self.calculate_season_score_cmd_ex

        if push_data.command_type == LeagueCommandType.PROCESS_WAIVERS:
            command = ProcessWaiversCommand(**push_data.command_data)
            executor = self.process_waivers_cmd_ex

        if push_data.command_type == LeagueCommandType.CALCULATE_PLAYOFFS:
            command = CalculatePlayoffsCommand(**push_data.command_data)
            executor = self.calculate_playoffs_cmd_ex

        return command, executor
