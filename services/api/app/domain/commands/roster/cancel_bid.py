
from services.api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from fastapi import Depends
from yards_py.core.annotate_args import annotate_args
from yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore


def create_cancel_bid_command_executor(
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
):
    return CancelBidCommandExecutor(
        league_roster_repo=league_roster_repo,
    )


@annotate_args
class CancelBidCommand(BaseCommand):
    league_id: str
    roster_id: str
    bid_index: int


@annotate_args
class CancelBidResult(BaseCommandResult[CancelBidCommand]):
    pass


class CancelBidCommandExecutor(BaseCommandExecutor[CancelBidCommand, CancelBidResult]):

    def __init__(
        self,
        league_roster_repo: LeagueRosterRepository,
    ):
        self.league_roster_repo = league_roster_repo

    def on_execute(self, command: CancelBidCommand) -> CancelBidResult:

        if command.roster_id != command.request_user_id:
            return CancelBidResult(command=command, error="Forbidden")

        @firestore.transactional
        def cancel_bid(transaction):
            roster = self.league_roster_repo.get(command.league_id, command.roster_id, transaction)

            if not roster:
                return CancelBidResult(command=command, error="Roster not found")

            roster.waiver_bids.pop(command.bid_index)

            self.league_roster_repo.set(command.league_id, roster, transaction)

            return CancelBidResult(command=command)

        transaction = self.league_roster_repo.firestore.create_transaction()
        return cancel_bid(transaction)
