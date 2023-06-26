
from app.yards_py.core.annotate_args import annotate_args
from app.yards_py.core.base_command_executor import (BaseCommand, BaseCommandExecutor,
                                                 BaseCommandResult)
from app.yards_py.domain.entities.league import League
from app.domain.repositories.league_repository import (
    LeagueRepository, create_league_repository)
from fastapi.param_functions import Depends
from google.cloud.firestore import Transaction
from firebase_admin.firestore import firestore


def create_set_notes_command_executor(
    league_repo: LeagueRepository = Depends(create_league_repository),
):
    return SetNotesCommandExecutor(
        league_repo=league_repo,
    )


@annotate_args
class SetNotesCommand(BaseCommand):
    league_id: str
    notes: str


@annotate_args
class SetNotesResult(BaseCommandResult):
    league: League


class SetNotesCommandExecutor(BaseCommandExecutor[SetNotesCommand, SetNotesResult]):

    def __init__(
        self,
        league_repo: LeagueRepository,
    ):
        self.league_repo = league_repo

    def on_execute(self, command: SetNotesCommand) -> SetNotesResult:
        @firestore.transactional
        def set_notes(transaction: Transaction):
            league = self.league_repo.get(command.league_id, transaction)

            if not league:
                return SetNotesResult(command=command, error="League not found")

            if not league.commissioner_id == command.request_user_id:
                return SetNotesResult(command=command, error="You are not the commissioner")

            league.notes = command.notes

            self.league_repo.update(league, transaction)
            return SetNotesResult(command=command, league=league)

        transaction = self.league_repo.firestore.create_transaction()
        return set_notes(transaction)
