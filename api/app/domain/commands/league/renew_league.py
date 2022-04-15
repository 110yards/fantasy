from api.app.domain.entities.user_league_preview import UserLeaguePreview
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from api.app.domain.repositories.league_owned_player_repository import LeagueOwnedPlayerRepository, create_league_owned_player_repository
from api.app.domain.repositories.league_player_score_repository import LeaguePlayerScoreRepository, create_league_player_score_repository
from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from api.app.domain.repositories.league_transaction_repository import LeagueTransactionRepository, create_league_transaction_repository
from api.app.domain.repositories.league_week_repository import LeagueWeekRepository, create_league_week_repository
from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository
from api.app.domain.repositories.user_archive_league_repository import UserArchiveLeagueRepository, create_user_archive_league_repository
from api.app.domain.repositories.user_league_repository import UserLeagueRepository, create_user_league_repository
from datetime import datetime

from api.app.core.annotate_args import annotate_args
from api.app.core.base_command_executor import (BaseCommand, BaseCommandExecutor,
                                                BaseCommandResult)
from api.app.domain.entities.league import (DraftState, League)
from api.app.domain.repositories.league_repository import (
    LeagueRepository, create_league_repository)
from fastapi.param_functions import Depends
from api.app.domain.repositories.user_repository import UserRepository, create_user_repository


def create_renew_league_command_executor(
    user_repo: UserRepository = Depends(create_user_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    user_league_repo: UserLeagueRepository = Depends(create_user_league_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
    league_week_repo: LeagueWeekRepository = Depends(create_league_week_repository),
    archive_league_repo: UserArchiveLeagueRepository = Depends(create_user_archive_league_repository),
    owned_player_repo: LeagueOwnedPlayerRepository = Depends(create_league_owned_player_repository),
    player_score_repo: LeaguePlayerScoreRepository = Depends(create_league_player_score_repository),
    transaction_repo: LeagueTransactionRepository = Depends(create_league_transaction_repository),

):
    return RenewLeagueCommandExecutor(
        user_repo=user_repo,
        archive_league_repo=archive_league_repo,
        league_config_repo=league_config_repo,
        league_repo=league_repo,
        league_roster_repo=league_roster_repo,
        league_week_repo=league_week_repo,
        owned_player_repo=owned_player_repo,
        player_score_repo=player_score_repo,
        transaction_repo=transaction_repo,
        user_league_repo=user_league_repo,
        public_repo=public_repo,
    )


@annotate_args
class RenewLeagueCommand(BaseCommand):
    league_id: str


@annotate_args
class RenewLeagueResult(BaseCommandResult):
    league: League


class RenewLeagueCommandExecutor(BaseCommandExecutor[RenewLeagueCommand, RenewLeagueResult]):

    def __init__(
        self,
        user_repo: UserRepository,
        league_repo: LeagueRepository,
        user_league_repo: UserLeagueRepository,
        league_roster_repo: LeagueRosterRepository,
        league_config_repo: LeagueConfigRepository,
        public_repo: PublicRepository,
        owned_player_repo: LeagueOwnedPlayerRepository,
        player_score_repo: LeaguePlayerScoreRepository,
        transaction_repo: LeagueTransactionRepository,
        league_week_repo: LeagueWeekRepository,
        archive_league_repo: UserArchiveLeagueRepository,
    ):
        self.league_repo = league_repo
        self.user_league_repo = user_league_repo
        self.league_roster_repo = league_roster_repo
        self.league_config_repo = league_config_repo
        self.public_repo = public_repo
        self.owned_player_repo = owned_player_repo
        self.player_score_repo = player_score_repo
        self.transaction_repo = transaction_repo
        self.league_week_repo = league_week_repo
        self.archive_league_repo = archive_league_repo

    def on_execute(self, command: RenewLeagueCommand) -> RenewLeagueResult:
        league = self.league_repo.get(command.league_id)

        if not league:
            return RenewLeagueResult(error="League not found")

        state = self.public_repo.get_state()

        league.season = state.current_season
        league.has_completed_season = True
        league.draft_state = DraftState.NOT_STARTED
        league.first_playoff_week = None
        league.renewed = datetime.now()
        league.schedule_generated = False

        schedule = self.league_config_repo.get_schedule_config(league.id)
        schedule.reset()
        self.league_config_repo.set_schedule_config(league.id, schedule)

        for owned_player in self.owned_player_repo.get_all(league.id):
            self.owned_player_repo.delete(league.id, owned_player.id)

        for score in self.player_score_repo.get_all(league.id):
            self.player_score_repo.delete(league.id, score.id)

        for transaction in self.transaction_repo.get_all(league.id):
            self.transaction_repo.delete(league.id, transaction.id)

        for week in self.league_week_repo.get_all(league.id):
            self.league_week_repo.delete(league.id, week.id)

        for roster in self.league_roster_repo.get_all(league.id):
            roster.reset()
            self.league_roster_repo.set(league.id, roster)
            preview = UserLeaguePreview.create(roster, league)
            self.user_league_repo.set(roster.id, preview)

        # save the league and remove the archive link last, in a transaction, in case something goes wrong.  Then the user can try again.
        self.league_repo.update(league)
        self.archive_league_repo.delete(league.commissioner_id, league.id)

        return RenewLeagueResult(command=command, league=league)
