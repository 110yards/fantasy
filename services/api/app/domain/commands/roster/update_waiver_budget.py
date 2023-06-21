
from services.api.app.domain.repositories.league_transaction_repository import LeagueTransactionRepository, create_league_transaction_repository
from yards_py.domain.entities.league_transaction import LeagueTransaction
from services.api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from services.api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from fastapi import Depends
from yards_py.core.annotate_args import annotate_args
from yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore


def create_update_waiver_budget_command_executor(
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_transaction_repo: LeagueTransactionRepository = Depends(create_league_transaction_repository),
):
    return UpdateWaiverBudgetCommandExecutor(
        league_repo=league_repo,
        league_roster_repo=league_roster_repo,
        league_transaction_repo=league_transaction_repo,
    )


@annotate_args
class UpdateWaiverBudgetCommand(BaseCommand):
    league_id: str
    roster_id: str
    waiver_budget: int
    current_user_id: str = ""


@annotate_args
class UpdateWaiverBudgetResult(BaseCommandResult[UpdateWaiverBudgetCommand]):
    pass


class UpdateWaiverBudgetCommandExecutor(BaseCommandExecutor[UpdateWaiverBudgetCommand, UpdateWaiverBudgetResult]):

    def __init__(
        self,
        league_repo: LeagueRepository,
        league_roster_repo: LeagueRosterRepository,
        league_transaction_repo: LeagueTransactionRepository,
    ):
        self.league_repo = league_repo
        self.league_roster_repo = league_roster_repo
        self.league_transaction_repo = league_transaction_repo

    def on_execute(self, command: UpdateWaiverBudgetCommand) -> UpdateWaiverBudgetResult:

        @firestore.transactional
        def update(transaction):
            league = self.league_repo.get(command.league_id, transaction)

            if not league:
                return UpdateWaiverBudgetResult(command=command, error="League not found")

            is_commissioner = league.commissioner_id == command.current_user_id

            if not is_commissioner:
                return UpdateWaiverBudgetResult(command=command, error="Forbidden")

            roster = self.league_roster_repo.get(command.league_id, command.roster_id, transaction)

            if not roster:
                return UpdateWaiverBudgetResult(command=command, error="Roster not found")

            old_budget = roster.copy().waiver_budget

            updates = {"waiver_budget": command.waiver_budget}
            self.league_roster_repo.partial_update(command.league_id, command.roster_id, updates, transaction)

            league_transaction = LeagueTransaction.change_waiver_budget(league.id, roster.id, roster.name, command.waiver_budget, old_budget)
            self.league_transaction_repo.create(command.league_id, league_transaction, transaction)

            return UpdateWaiverBudgetResult(command=command)

        transaction = self.league_roster_repo.firestore.create_transaction()
        return update(transaction)
