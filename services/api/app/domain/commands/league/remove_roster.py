
from app.domain.enums.draft_state import DraftState
from app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.domain.repositories.user_league_repository import UserLeagueRepository, create_user_league_repository
from app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from fastapi import Depends
from app.yards_py.core.annotate_args import annotate_args
from app.yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore


def create_remove_roster_command_executor(
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    user_league_repo: UserLeagueRepository = Depends(create_user_league_repository),
):
    return RemoveRosterCommandExecutor(league_repo, league_roster_repo, user_league_repo)


@annotate_args
class RemoveRosterCommand(BaseCommand):
    league_id: str
    roster_id: str


@annotate_args
class RemoveRosterResult(BaseCommandResult[RemoveRosterCommand]):
    pass


class RemoveRosterCommandExecutor(BaseCommandExecutor[RemoveRosterCommand, RemoveRosterResult]):

    def __init__(self,
                 league_repo: LeagueRepository,
                 league_roster_repo: LeagueRosterRepository,
                 user_league_repo: UserLeagueRepository,
                 ):
        self.league_repo = league_repo
        self.league_roster_repo = league_roster_repo
        self.user_league_repo = user_league_repo

    def on_execute(self, command: RemoveRosterCommand) -> RemoveRosterResult:

        @firestore.transactional
        def remove(transaction):
            # TODO: put this in a service, and use it in the delete league cmd ex
            league = self.league_repo.get(command.league_id, transaction)

            if league.draft_state != DraftState.NOT_STARTED:
                return RemoveRosterResult(command=command, error="Can't remove teams after the draft has started")

            league.schedule_generated = False

            if not league.roster_count:
                # added for #164 - if it's not set, it's an old league as we need to count
                rosters = self.league_roster_repo.get_all(command.league_id)
                league.roster_count = len(rosters)

            league.roster_count -= 1

            league.draft_order = [item for item in league.draft_order if item.roster_id != command.roster_id]

            self.league_repo.update(league, transaction)
            self.league_roster_repo.delete(command.league_id, command.roster_id, transaction)
            self.user_league_repo.delete(command.roster_id, command.league_id, transaction)

            return RemoveRosterResult(command=command)

        transaction = self.league_roster_repo.firestore.create_transaction()
        return remove(transaction)
