
from yards_py.domain.entities.draft import DraftOrder
from services.api.app.domain.repositories.user_league_repository import UserLeagueRepository, create_user_league_repository
from yards_py.domain.entities.user_league_preview import UserLeaguePreview
from yards_py.domain.entities.roster import Roster
from services.api.app.domain.repositories.user_repository import UserRepository, create_user_repository
from services.api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from services.api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from services.api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from typing import Optional
from fastapi import Depends
from yards_py.core.annotate_args import annotate_args
from yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore

MAX_ROSTER_COUNT = 10


def create_join_league_command_executor(
        league_repo: LeagueRepository = Depends(create_league_repository),
        league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
        league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
        user_repo: UserRepository = Depends(create_user_repository),
        user_league_repo: UserLeagueRepository = Depends(create_user_league_repository),
):
    return JoinLeagueCommandExecutor(league_repo, league_config_repo, league_roster_repo, user_repo, user_league_repo)


@annotate_args
class JoinLeagueCommand(BaseCommand):
    league_id: Optional[str]
    user_id: Optional[str]
    password: Optional[str]


@annotate_args
class JoinLeagueResult(BaseCommandResult[JoinLeagueCommand]):
    roster: Optional[Roster]


class JoinLeagueCommandExecutor(BaseCommandExecutor[JoinLeagueCommand, BaseCommandResult]):

    def __init__(
        self,
        league_repo: LeagueRepository,
        league_config_repo: LeagueConfigRepository,
        league_roster_repo: LeagueRosterRepository,
        user_repo: UserRepository,
        user_league_repo: UserLeagueRepository,
    ):
        self.league_repo = league_repo
        self.league_config_repo = league_config_repo
        self.league_roster_repo = league_roster_repo
        self.user_repo = user_repo
        self.user_league_repo = user_league_repo

    def on_execute(self, command: JoinLeagueCommand) -> BaseCommandResult:

        @firestore.transactional
        def join(transaction):
            league = self.league_repo.get(command.league_id, transaction)

            if not league:
                return JoinLeagueResult(command=command, error="League not found")

            if league.registration_closed:
                return JoinLeagueResult(command=command, error="Registration is closed")

            private_config = self.league_config_repo.get_private_config(command.league_id, transaction)

            if private_config.password and command.password != private_config.password:
                return JoinLeagueResult(command=command, error="Incorrect password")

            manager = self.user_repo.get(command.user_id, transaction)

            if not league.roster_count:
                # added for #164 - if it's not set, it's an old league as we need to count
                rosters = self.league_roster_repo.get_all(command.league_id)
                league.roster_count = len(rosters)

            if league.roster_count > MAX_ROSTER_COUNT:
                return JoinLeagueResult(command=command, error=f"Sorry, but this league is full (max = {MAX_ROSTER_COUNT} teams)")

            league.roster_count += 1
            roster = create_roster(manager.id, manager.display_name)
            user_league_preview = UserLeaguePreview.create(roster, league)
            league.draft_order.append(DraftOrder(roster_id=manager.id))
            league.schedule_generated = False

            self.league_repo.update(league, transaction)
            self.league_roster_repo.set(league.id, roster, transaction)
            self.user_league_repo.set(manager.id, user_league_preview, transaction)

            return JoinLeagueResult(command=command, roster=roster)

        transaction = self.league_repo.firestore.create_transaction()
        return join(transaction)


def create_roster(user_id, display_name) -> Roster:
    return Roster(
        id=user_id,
        name=f"Team {display_name}"
    )
