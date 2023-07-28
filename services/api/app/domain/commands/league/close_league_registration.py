from typing import Optional

from fastapi import Depends
from firebase_admin import firestore

from app.core.annotate_args import annotate_args
from app.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from app.domain.entities.league import League
from app.domain.repositories.league_repository import LeagueRepository, create_league_repository


def create_close_league_registration_command_executor(league_repo: LeagueRepository = Depends(create_league_repository)):
    return CloseLeagueRegistrationCommandExecutor(league_repo)


@annotate_args
class CloseLeagueRegistrationCommand(BaseCommand):
    league_id: str


@annotate_args
class CloseLeagueRegistrationResult(BaseCommandResult[CloseLeagueRegistrationCommand]):
    league: Optional[League]


class CloseLeagueRegistrationCommandExecutor(BaseCommandExecutor[CloseLeagueRegistrationCommand, CloseLeagueRegistrationResult]):
    def __init__(self, league_repo: LeagueRepository):
        self.league_repo = league_repo

    def on_execute(self, command: CloseLeagueRegistrationCommand) -> CloseLeagueRegistrationResult:
        @firestore.transactional
        def update(transaction):
            league = self.league_repo.get(command.league_id, transaction)
            if not league:
                return CloseLeagueRegistrationResult(command=command, error="League not found")

            league.registration_closed = True
            league = self.league_repo.update(league, transaction)

            return CloseLeagueRegistrationResult(command=command, league=league)

        transaction = self.league_repo.firestore.create_transaction()
        return update(transaction)
