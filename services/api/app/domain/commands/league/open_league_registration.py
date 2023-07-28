from typing import Optional

from fastapi import Depends
from firebase_admin import firestore

from app.core.annotate_args import annotate_args
from app.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from app.domain.entities.league import League
from app.domain.enums.draft_state import DraftState
from app.domain.repositories.league_repository import LeagueRepository, create_league_repository


def create_open_league_registration_command_executor(league_repo: LeagueRepository = Depends(create_league_repository)):
    return OpenLeagueRegistrationCommandExecutor(league_repo)


@annotate_args
class OpenLeagueRegistrationCommand(BaseCommand):
    league_id: str


@annotate_args
class OpenLeagueRegistrationResult(BaseCommandResult[OpenLeagueRegistrationCommand]):
    league: Optional[League]


class OpenLeagueRegistrationCommandExecutor(BaseCommandExecutor[OpenLeagueRegistrationCommand, OpenLeagueRegistrationResult]):
    def __init__(self, league_repo: LeagueRepository):
        self.league_repo = league_repo

    def on_execute(self, command: OpenLeagueRegistrationCommand) -> OpenLeagueRegistrationResult:
        @firestore.transactional
        def update(transaction):
            league = self.league_repo.get(command.league_id, transaction)
            if not league:
                return OpenLeagueRegistrationResult(command=command, error="League not found")

            if not league.draft_state == DraftState.NOT_STARTED:
                return OpenLeagueRegistrationResult(command=command, error="Registration cannot be opened after league has started")

            league.registration_closed = False
            league = self.league_repo.update(league, transaction)

            return OpenLeagueRegistrationResult(command=command, league=league)

        transaction = self.league_repo.firestore.create_transaction()
        return update(transaction)
