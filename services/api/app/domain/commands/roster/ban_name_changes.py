
from app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from typing import Optional
from fastapi import Depends
from app.yards_py.core.annotate_args import annotate_args
from app.yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore


def create_set_name_change_ban_command_executor(
        league_repo: LeagueRepository = Depends(create_league_repository),
        league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
):
    return SetNameChangeBanCommandExecutor(
        league_repo=league_repo,
        league_roster_repo=league_roster_repo
    )


@annotate_args
class SetNameChangeBanCommand(BaseCommand):
    league_id: str
    roster_id: str
    banned: bool
    current_user_id: Optional[str]


@annotate_args
class SetNameChangeBanResult(BaseCommandResult[SetNameChangeBanCommand]):
    pass


class SetNameChangeBanCommandExecutor(BaseCommandExecutor[SetNameChangeBanCommand, SetNameChangeBanResult]):

    def __init__(
        self,
        league_repo: LeagueRepository,
        league_roster_repo: LeagueRosterRepository,
    ):
        self.league_repo = league_repo
        self.league_roster_repo = league_roster_repo

    def on_execute(self, command: SetNameChangeBanCommand) -> SetNameChangeBanResult:

        @firestore.transactional
        def update(transaction):
            league = self.league_repo.get(command.league_id, transaction)

            if not league:
                return SetNameChangeBanResult(command=command, error="League not found")

            is_commissioner = league.commissioner_id == command.current_user_id

            if is_commissioner:
                return SetNameChangeBanResult(command=command, error="Forbidden")

            roster = self.league_roster_repo.get(command.league_id, command.roster_id, transaction)
            roster.name_changes_banned = command.banned

            self.league_roster_repo.set(command.league_id, roster, transaction)

            return SetNameChangeBanResult(command=command)

        transaction = self.league_roster_repo.firestore.create_transaction()
        return update(transaction)
