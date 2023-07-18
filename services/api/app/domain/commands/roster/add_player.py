
from yards_py.domain.entities.league import League
from yards_py.domain.entities.league_transaction import LeagueTransaction
from services.api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from yards_py.domain.entities.waiver_bid import WaiverBid
from services.api.app.domain.repositories.state_repository import StateRepository, create_state_repository
from services.api.app.domain.repositories.player_repository import PlayerRepository, create_player_repository
from services.api.app.domain.services.notification_service import NotificationService, create_notification_service
from services.api.app.domain.services.roster_player_service import RosterPlayerService, create_roster_player_service
from typing import List, Optional
from services.api.app.domain.repositories.league_owned_player_repository import LeagueOwnedPlayerRepository, create_league_owned_player_repository
from services.api.app.domain.repositories.league_transaction_repository import LeagueTransactionRepository, create_league_transaction_repository
from services.api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from fastapi import Depends
from yards_py.core.annotate_args import annotate_args
from yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore


def create_add_player_command_executor(
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    league_transaction_repo: LeagueTransactionRepository = Depends(create_league_transaction_repository),
    league_owned_players_repo: LeagueOwnedPlayerRepository = Depends(create_league_owned_player_repository),
    player_repo: PlayerRepository = Depends(create_player_repository),
    roster_player_service: RosterPlayerService = Depends(create_roster_player_service),
    state_repo: StateRepository = Depends(create_state_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    notification_service: NotificationService = Depends(create_notification_service),
):
    return AddPlayerCommandExecutor(
        league_roster_repo=league_roster_repo,
        league_transaction_repo=league_transaction_repo,
        league_owned_players_repo=league_owned_players_repo,
        player_repo=player_repo,
        roster_player_service=roster_player_service,
        state_repo=state_repo,
        league_repo=league_repo,
        notification_service=notification_service,
    )


@annotate_args
class AddPlayerCommand(BaseCommand):
    league_id: str
    roster_id: str
    player_id: str
    drop_player_id: Optional[str]
    bid: Optional[int]
    admin_override: bool = False


@annotate_args
class AddPlayerResult(BaseCommandResult[AddPlayerCommand]):
    league: Optional[League]
    transactions: List[LeagueTransaction] = None


class AddPlayerCommandExecutor(BaseCommandExecutor[AddPlayerCommand, AddPlayerResult]):

    def __init__(
        self,
        league_roster_repo: LeagueRosterRepository,
        league_transaction_repo: LeagueTransactionRepository,
        league_owned_players_repo: LeagueOwnedPlayerRepository,
        roster_player_service: RosterPlayerService,
        player_repo: PlayerRepository,
        state_repo: StateRepository,
        league_repo: LeagueRepository,
        notification_service: NotificationService,
    ):
        self.league_roster_repo = league_roster_repo
        self.league_transaction_repo = league_transaction_repo
        self.league_owned_players_repo = league_owned_players_repo
        self.roster_player_service = roster_player_service
        self.player_repo = player_repo
        self.state_repo = state_repo
        self.league_repo = league_repo
        self.notification_service = notification_service

    def on_execute(self, command: AddPlayerCommand) -> AddPlayerResult:

        for_users_roster = command.roster_id == command.request_user_id
        if not for_users_roster and not command.admin_override:  # TODO: allow commissioner to make moves
            return AddPlayerResult(command=command, error="Forbidden")

        state = self.state_repo.get()  # don't lock state

        @firestore.transactional
        def update(transaction):
            league = self.league_repo.get(command.league_id, transaction)
            roster = self.league_roster_repo.get(command.league_id, command.roster_id, transaction)

            if not roster:
                return AddPlayerResult(command=command, error="Roster not found")

            current_owner = self.league_owned_players_repo.get(command.league_id, command.player_id, transaction)

            if current_owner:
                return AddPlayerResult(command=command, error="That player is already on a roster")

            player = self.player_repo.get(state.current_season, command.player_id, transaction)

            if not player:
                return AddPlayerResult(command=command, error="Player not found")

            if state.locks.is_locked(player.team) and not command.admin_override:
                return AddPlayerResult(command=command, error=f"{player.team.location} players are locked")

            target_position = None
            if command.drop_player_id:
                target_position = roster.find_player_position(command.drop_player_id)

            if state.waivers_active:
                bid = WaiverBid(roster_id=command.roster_id, player=player, amount=command.bid)
                if command.drop_player_id:
                    bid.drop_player = target_position.player

                roster.waiver_bids.append(bid)
                roster.waiver_bids.sort(key=lambda x: x.amount, reverse=True)
                self.league_roster_repo.update(command.league_id, roster, transaction)

                return AddPlayerResult(command=command)

            elif not state.waivers_active and league.waivers_active:
                return AddPlayerResult(command=command, error="Waivers are still being processed for your league, please try again in a few minutes. "
                                       + "If you see this message for more than a few minutes, please contact the site administrator.")

            else:
                if not target_position:
                    target_position = self.roster_player_service.find_position_for(player, roster)

                if not target_position:
                    return AddPlayerResult(command=command, error=f"There is no space on roster for a {player.position.display_name()}")

                success, info = self.roster_player_service.assign_player_to_roster(
                    league_id=command.league_id,
                    roster=roster,
                    player=player,
                    target_position=target_position,
                    record_transaction=True,
                    transaction=transaction
                )

                if success:
                    return AddPlayerResult(command=command, league=league, transactions=info)
                else:
                    return AddPlayerResult(command=command, error=info)

        transaction = self.league_roster_repo.firestore.create_transaction()
        result = update(transaction)

        if result.success and result.transactions:
            if len(result.transactions) == 1:
                message = result.transactions[0].message
            else:
                message = result.transactions[0].message + " and " + result.transactions[1].message

            self.notification_service.send_transaction_event(result.league, message)

        return result
