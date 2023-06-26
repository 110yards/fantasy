
from typing import Optional
from app.yards_py.domain.entities.league import League
from app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.domain.repositories.state_repository import StateRepository, create_state_repository
from app.yards_py.domain.entities.league_transaction import LeagueTransaction
from app.domain.repositories.league_owned_player_repository import LeagueOwnedPlayerRepository, create_league_owned_player_repository
from app.domain.repositories.league_transaction_repository import LeagueTransactionRepository, create_league_transaction_repository
from app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from fastapi import Depends
from app.yards_py.core.annotate_args import annotate_args
from app.yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore

from app.domain.services.notification_service import NotificationService, create_notification_service


def create_drop_player_command_executor(
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    league_transaction_repo: LeagueTransactionRepository = Depends(create_league_transaction_repository),
    league_owned_players_repo: LeagueOwnedPlayerRepository = Depends(create_league_owned_player_repository),
    state_repo: StateRepository = Depends(create_state_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    notification_service: NotificationService = Depends(create_notification_service),
):
    return DropPlayerCommandExecutor(
        league_roster_repo=league_roster_repo,
        league_transaction_repo=league_transaction_repo,
        league_owned_players_repo=league_owned_players_repo,
        state_repo=state_repo,
        league_repo=league_repo,
        notification_service=notification_service,
    )


@annotate_args
class DropPlayerCommand(BaseCommand):
    league_id: str
    roster_id: str
    player_id: str


@annotate_args
class DropPlayerResult(BaseCommandResult[DropPlayerCommand]):
    league: Optional[League]
    transaction: Optional[LeagueTransaction]


class DropPlayerCommandExecutor(BaseCommandExecutor[DropPlayerCommand, DropPlayerResult]):

    def __init__(
        self,
        league_roster_repo: LeagueRosterRepository,
        league_transaction_repo: LeagueTransactionRepository,
        league_owned_players_repo: LeagueOwnedPlayerRepository,
        state_repo: StateRepository,
        league_repo: LeagueRepository,
        notification_service: NotificationService,
    ):
        self.league_roster_repo = league_roster_repo
        self.league_transaction_repo = league_transaction_repo
        self.league_owned_players_repo = league_owned_players_repo
        self.state_repo = state_repo
        self.league_repo = league_repo
        self.notification_service = notification_service

    def on_execute(self, command: DropPlayerCommand) -> DropPlayerResult:

        @firestore.transactional
        def update(transaction):
            roster = self.league_roster_repo.get(command.league_id, command.roster_id, transaction)

            if not roster:
                return DropPlayerResult(command=command, error="Roster not found")

            league = self.league_repo.get(command.league_id, transaction)

            if not league:
                return DropPlayerResult(command=command, error="League not found")

            is_for_self = command.roster_id == command.request_user_id
            is_commissioner = command.request_user_id == league.commissioner_id

            if not is_for_self and not is_commissioner:
                return DropPlayerResult(command=command, error="Forbidden")

            is_commissioner_override = not is_for_self and is_commissioner

            roster_position = roster.find_player_position(command.player_id)

            if not roster_position:
                return DropPlayerResult(command=command, error="That player is not on your roster")

            state = self.state_repo.get()
            if state.locks.is_locked(roster_position.player.team):
                return DropPlayerResult(command=command, error=f"{roster_position.player.team.location} players are locked")

            league_transaction = LeagueTransaction.drop_transaction(command.league_id, roster, roster_position.player, is_commissioner_override)
            roster_position.player = None
            roster.active_player_count -= 1

            self.league_roster_repo.update(command.league_id, roster, transaction)
            self.league_transaction_repo.create(command.league_id, league_transaction, transaction)
            self.league_owned_players_repo.delete(command.league_id, command.player_id, transaction)

            return DropPlayerResult(command=command, league=league, transaction=league_transaction)

        transaction = self.league_roster_repo.firestore.create_transaction()
        result = update(transaction)

        if result.success:
            self.notification_service.send_transaction_event(result.league, result.transaction.message)

        return result
