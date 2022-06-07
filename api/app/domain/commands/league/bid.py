from api.app.domain.services.auction_draft_service import AuctionDraftService, create_auction_draft_service
from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from fastapi import Depends
from yards_py.core.annotate_args import annotate_args
from yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore


def create_bid_command_executor(
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    auction_draft_service=Depends(create_auction_draft_service),
):
    return BidCommandExecutor(league_config_repo, league_roster_repo, auction_draft_service)


@annotate_args
class BidCommand(BaseCommand):
    league_id: str
    pick_number: int
    bidder: str
    bid_amount: int


@annotate_args
class BidResult(BaseCommandResult[BidCommand]):
    pass


class BidCommandExecutor(BaseCommandExecutor[BidCommand, BidResult]):

    def __init__(
            self,
            league_config_repo: LeagueConfigRepository,
            league_roster_repo: LeagueRosterRepository,
            auction_draft_service: AuctionDraftService,
    ):
        self.league_config_repo = league_config_repo
        self.league_roster_repo = league_roster_repo
        self.auction_draft_service = auction_draft_service

    def on_execute(self, command: BidCommand) -> BidResult:

        pick_index = command.pick_number - 1

        @firestore.transactional
        def update(transaction):
            draft = self.league_config_repo.get_draft(command.league_id, transaction)

            if command.pick_number > len(draft.slots):
                return BidResult(command=command, error="Invalid pick")

            slot = draft.slots[pick_index]

            if slot.completed:
                return BidResult(command=command, error="That pick has already been completed")

            bidder_index = slot.bidder_index  # type: int
            current_bidder = slot.bidders[bidder_index]
            if current_bidder.roster_id != command.bidder:
                return BidResult(command=command, error="It's not your turn")

            if slot.bid >= command.bid_amount:
                return BidResult(command=command, error=f"Minimum bid is ${slot.bid + 1}")

            rosters = self.league_roster_repo.get_all(command.league_id, transaction)
            rosters = {roster.id: roster for roster in rosters}

            if rosters[command.bidder].draft_budget < command.bid_amount:
                return BidResult(command=command, error="You do not have enough money left to place that bid")

            for bidder in slot.bidders:
                roster = rosters[bidder.roster_id]
                if roster.draft_budget < command.bid_amount:
                    bidder.outbid = True

            slot.bid = command.bid_amount
            slot.roster_id = command.bidder

            next_bidder = slot.get_next_bidder(bidder_index)
            won = next_bidder is None

            if not won:
                slot.bidder_index = next_bidder.index
            else:
                result = self.auction_draft_service.complete_slot(command.league_id, draft, slot, command.bidder, transaction)
                if not result.success:
                    return BidResult(command=command, error=result.error)

                self.league_roster_repo.set(command.league_id, roster, transaction)

            draft.slots[pick_index] = slot
            self.league_config_repo.set_draft(command.league_id, draft, transaction)

            return BidResult(command=command)

        transaction = self.league_config_repo.firestore.create_transaction()
        return update(transaction)
