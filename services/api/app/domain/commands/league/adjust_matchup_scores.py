
from ......system.app.domain.services.league_command_push_data import LeagueCommandPushData
from yards_py.domain.enums.league_command_type import LeagueCommandType
from yards_py.core.logging import Logger
from yards_py.domain.topics import LEAGUE_COMMAND_TOPIC
from ....di import create_publisher
from yards_py.core.base_command_executor import (BaseCommand, BaseCommandExecutor,
                                                 BaseCommandResult)
from yards_py.core.publisher import Publisher
from yards_py.domain.entities.league import League
from services.api.app.domain.repositories.league_repository import (
    LeagueRepository, create_league_repository)
from fastapi.param_functions import Depends
from google.cloud.firestore import Transaction
from firebase_admin.firestore import firestore

from yards_py.domain.entities.league_transaction import LeagueTransaction

from yards_py.domain.repositories.league_transaction_repository import LeagueTransactionRepository, create_league_transaction_repository
from yards_py.domain.repositories.league_week_matchup_repository import LeagueWeekMatchupRepository, create_league_week_matchup_repository
from yards_py.domain.repositories.user_repository import UserRepository, create_user_repository




class AdjustMatchupScoresCommand(BaseCommand):
    league_id: str
    week_number: int
    matchup_id: str
    away_adjustment: int
    home_adjustment: int


class AdjustMatchupScoresResult(BaseCommandResult):
    league: League


class AdjustMatchupScoresCommandExecutor(BaseCommandExecutor[AdjustMatchupScoresCommand, AdjustMatchupScoresResult]):

    def __init__(
        self,
        league_repo: LeagueRepository,
        matchup_repository: LeagueWeekMatchupRepository,
        user_repo: UserRepository,
        transaction_repo: LeagueTransactionRepository,
        publisher: Publisher
    ):
        self.league_repo = league_repo
        self.matchup_repository = matchup_repository
        self.user_repo = user_repo
        self.transaction_repo = transaction_repo
        self.publisher = publisher

    def on_execute(self, command: AdjustMatchupScoresCommand) -> AdjustMatchupScoresResult:

        # make sure this is the commissioner or admin
        league = self.league_repo.get(command.league_id)

        if not league:
            return AdjustMatchupScoresResult(command=command, error="League not found")
        
        is_commissioner = league.commissioner_id == command.request_user_id

        if not is_commissioner:
            user = self.user_repo.get(command.request_user_id)
            if not user.is_admin:
                return AdjustMatchupScoresResult(command=command, error="Forbidden")


        @firestore.transactional
        def apply_adjustment(transaction: Transaction) -> AdjustMatchupScoresResult:

            matchup = self.matchup_repository.get(command.league_id, command.week_number, command.matchup_id, transaction=transaction)

            if not matchup:
                return AdjustMatchupScoresResult(command=command, error="Matchup not found")
            
            matchup.away_adjustment = command.away_adjustment
            matchup.home_adjustment = command.home_adjustment

            league_transaction = LeagueTransaction.commissioner_adjust_result(
                league_id=command.league_id,
                week_number=command.week_number,
                away_name=matchup.away.name,
                away_adjustment=command.away_adjustment,
                home_name=matchup.home.name,
                home_adjustment=command.home_adjustment,
            )

            self.transaction_repo.create(command.league_id, league_transaction, transaction=transaction)
            self.matchup_repository.set(command.league_id, command.week_number, matchup, transaction=transaction)

            return AdjustMatchupScoresResult(command=command, league=league)
        


        transaction = self.league_repo.firestore.create_transaction()
        result = apply_adjustment(transaction)

        if not result.success:
            return result
        
        payload = LeagueCommandPushData(command_type=LeagueCommandType.CALCULATE_RESULTS, command_data=
                                        {
                                            "league_id": command.league_id,
                                            "week_number": command.week_number,
                                            "pass_week": True
                                        })

        try:
            self.publisher.publish(payload, LEAGUE_COMMAND_TOPIC)
        except Exception as ex:
            Logger.error("Error publishing recalculation command", exc_info=ex)
            return AdjustMatchupScoresResult(command=command, error="An error occured publishing the recalculation command, please try again or contact the administrator")



def create_adjust_matchup_scores_command_executor(
    league_repo: LeagueRepository = Depends(create_league_repository),
    matchup_repository: LeagueWeekMatchupRepository = Depends(create_league_week_matchup_repository),
    user_repo: UserRepository = Depends(create_user_repository),
    transaction_repo: LeagueTransactionRepository = Depends(create_league_transaction_repository),
    publisher: Publisher = Depends(create_publisher),
):
    return AdjustMatchupScoresCommandExecutor(
        league_repo=league_repo,
        matchup_repository=matchup_repository,
        user_repo=user_repo,
        transaction_repo=transaction_repo,
        publisher=publisher
    )
