
from api.app.domain.repositories.state_repository import StateRepository, create_state_repository
from api.app.domain.services.auction_draft_service import AuctionDraftService, create_auction_draft_service
from api.app.domain.services.roster_player_service import RosterPlayerService, create_roster_player_service
from api.app.domain.repositories.player_repository import PlayerRepository, create_player_repository
from api.app.domain.repositories.league_owned_player_repository import LeagueOwnedPlayerRepository, create_league_owned_player_repository
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from fastapi import Depends
from yards_py.core.annotate_args import annotate_args
from yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore


def create_nominate_player_command_executor(
    state_repo: StateRepository = Depends(create_state_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    league_owned_player_repo: LeagueOwnedPlayerRepository = Depends(create_league_owned_player_repository),
    player_repo: PlayerRepository = Depends(create_player_repository),
    roster_player_service: RosterPlayerService = Depends(create_roster_player_service),
    auction_draft_service: AuctionDraftService = Depends(create_auction_draft_service),
):
    return NominatePlayerCommandExecutor(
        state_repo,
        league_config_repo,
        league_owned_player_repo,
        player_repo,
        roster_player_service,
        auction_draft_service=auction_draft_service
    )


@annotate_args
class NominatePlayerCommand(BaseCommand):
    pick_number: int
    nominator: str
    league_id: str
    player_id: str


@annotate_args
class NominatePlayerResult(BaseCommandResult[NominatePlayerCommand]):
    pass


class NominatePlayerCommandExecutor(BaseCommandExecutor[NominatePlayerCommand, NominatePlayerResult]):

    def __init__(
        self,
        state_repo: StateRepository,
        league_config_repo: LeagueConfigRepository,
        league_owned_player_repo: LeagueOwnedPlayerRepository,
        player_repo: PlayerRepository,
        roster_player_service: RosterPlayerService,
        auction_draft_service: AuctionDraftService,
    ):
        self.state_repo = state_repo
        self.league_config_repo = league_config_repo
        self.league_owned_player_repo = league_owned_player_repo
        self.player_repo = player_repo
        self.roster_player_service = roster_player_service
        self.auction_draft_service = auction_draft_service

    def on_execute(self, command: NominatePlayerCommand) -> NominatePlayerResult:
        # confirm player not yet taken
        existing = self.league_owned_player_repo.get(command.league_id, command.player_id)

        if existing:
            return NominatePlayerResult(command=command, error="Player has already been drafted")

        state = self.state_repo = self.state_repo.get()

        player = self.player_repo.get(state.current_season, command.player_id)

        if not player:
            return NominatePlayerResult(command=command, error="Player does not exist")

        pick_index = command.pick_number - 1

        @firestore.transactional
        def update(transaction):
            draft = self.league_config_repo.get_draft(command.league_id, transaction)

            if len(draft.slots) < command.pick_number:
                return NominatePlayerResult(command=command, error="Invalid draft slot")

            slot = draft.slots[pick_index]

            if slot.completed:
                return NominatePlayerResult(command=command, error="Draft slot has already been used")

            if slot.nominator != command.nominator:
                return NominatePlayerResult(command=command, error="It's not your turn")

            potential_position = self.roster_player_service.find_position_for(player, command.league_id, command.nominator, transaction)

            if not potential_position:
                return NominatePlayerResult(command=command, error=f"There is no space on your roster for a {player.position.display_name()}")

            slot.player = player
            slot.bid = 0
            slot.roster_id = command.nominator

            for bidder in slot.bidders:
                if bidder.roster_id == command.nominator:
                    continue

                potential_position = self.roster_player_service.find_position_for(player, command.league_id, bidder.roster_id, transaction)
                if not potential_position:
                    bidder.in_eligible = True

            eligible_bidders = [bidder for bidder in slot.bidders if not bidder.in_eligible]

            no_other_bidders = len(eligible_bidders) == 1

            if no_other_bidders:
                result = self.auction_draft_service.complete_slot(command.league_id, draft, slot, command.nominator, transaction)
                if not result.success:
                    return NominatePlayerResult(command=command, error=result.error)

            else:
                slot.bidder_index = slot.get_next_bidder(-1).index

            self.league_config_repo.set_draft(command.league_id, draft, transaction)

            return NominatePlayerResult(command=command)

        transaction = self.league_config_repo.firestore.create_transaction()
        return update(transaction)
