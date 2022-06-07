from api.app.domain.repositories.league_week_repository import LeagueWeekRepository
from api.app.domain.repositories.league_week_matchup_repository import LeagueWeekMatchupRepository
from api.app.domain.repositories.league_transaction_repository import LeagueTransactionRepository
from api.app.domain.repositories.player_league_season_score_repository import PlayerLeagueSeasonScoreRepository
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from api.app.domain.repositories.user_league_repository import UserLeagueRepository, create_user_league_repository

from yards_py.core.annotate_args import annotate_args
from yards_py.core.base_command_executor import (BaseCommand, BaseCommandExecutor,
                                                 BaseCommandResult)
from yards_py.core.publisher import Publisher, create_publisher
from yards_py.domain.entities.league import (League)
from api.app.domain.repositories.league_repository import (
    LeagueRepository, create_league_repository)
from fastapi.param_functions import Depends
from firebase_admin.firestore import firestore
from api.app.domain.repositories.user_repository import UserRepository, create_user_repository


def create_delete_league_command_executor(
    user_repo: UserRepository = Depends(create_user_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    user_league_repo: UserLeagueRepository = Depends(create_user_league_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    publisher: Publisher = Depends(create_publisher),
):
    return DeleteLeagueCommandExecutor(
        user_repo,
        league_repo,
        user_league_repo,
        league_roster_repo,
        league_config_repo,
        publisher)


@annotate_args
class DeleteLeagueCommand(BaseCommand):
    league_id: str


@annotate_args
class DeleteLeagueResult(BaseCommandResult[DeleteLeagueCommand]):
    league: League


class DeleteLeagueCommandExecutor(BaseCommandExecutor[DeleteLeagueCommand, DeleteLeagueResult]):

    def __init__(
        self,
        league_repo: LeagueRepository,
        user_league_repo: UserLeagueRepository,
        league_config_repo: LeagueConfigRepository,
        league_player_score_repo: PlayerLeagueSeasonScoreRepository,
        league_roster_repo: LeagueRosterRepository,
        league_transaction_repo: LeagueTransactionRepository,
        league_week_matchup_repo: LeagueWeekMatchupRepository,
        league_week_repo: LeagueWeekRepository,
    ):
        self.league_repo = league_repo
        self.user_league_repo = user_league_repo
        self.league_config_repo = league_config_repo
        self.league_player_score_repo = league_player_score_repo
        self.league_roster_repo = league_roster_repo
        self.league_transaction_repo = league_transaction_repo
        self.league_week_matchup_repo = league_week_matchup_repo
        self.league_week_repo = league_week_repo

    def on_execute(self, command: DeleteLeagueCommand) -> DeleteLeagueResult:

        @firestore.transactional
        def delete(transaction):
            league = self.league_repo.get(command.league_id)

            if not league:
                return DeleteLeagueResult(command=command, error="League not found")

        transaction = self.league_repo.firestore.create_transaction()
        return delete(transaction)
