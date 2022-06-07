
from services.api.app.domain.services.auction_draft_service import AuctionDraftService, create_auction_draft_service
from services.api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from fastapi import Depends
from yards_py.core.annotate_args import annotate_args
from yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore


def create_pass_bid_command_executor(
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    auction_draft_service: AuctionDraftService = Depends(create_auction_draft_service)
):
    return PassBidCommandExecutor(league_config_repo, auction_draft_service)


@annotate_args
class PassBidCommand(BaseCommand):
    league_id: str
    bidder: str
    pick_number: int


@annotate_args
class PassBidResult(BaseCommandResult[PassBidCommand]):
    pass


class PassBidCommandExecutor(BaseCommandExecutor[PassBidCommand, PassBidResult]):

    def __init__(
        self,
        league_config_repo: LeagueConfigRepository,
        auction_draft_service: AuctionDraftService,
    ):
        self.league_config_repo = league_config_repo
        self.auction_draft_service = auction_draft_service

    def on_execute(self, command: PassBidCommand) -> PassBidResult:

        pick_index = command.pick_number - 1

        @firestore.transactional
        def update(transaction):
            draft = self.league_config_repo.get_draft(command.league_id, transaction)

            if command.pick_number > len(draft.slots):
                return PassBidResult(command=command, error="Invalid pick")

            slot = draft.slots[pick_index]

            bidder_index = slot.bidder_index  # type: int
            current_bidder = slot.bidders[bidder_index]

            if current_bidder.roster_id != command.bidder:
                return PassBidResult(command=command, error="It's not your turn")

            current_bidder.passed = True

            next_bidder = slot.get_next_bidder(bidder_index)

            over = next_bidder is None

            if over:
                result = self.auction_draft_service.complete_slot(command.league_id, draft, slot, slot.roster_id, transaction)

                if not result.success:
                    return PassBidResult(command=command, error=result.error)

            self.league_config_repo.set_draft(command.league_id, draft, transaction)

            return PassBidResult(command=command)

        transaction = self.league_config_repo.firestore.create_transaction()
        return update(transaction)
