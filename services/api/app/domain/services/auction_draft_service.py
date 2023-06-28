from typing import Optional

from fastapi import Depends
from google.cloud.firestore_v1.transaction import Transaction
from pydantic.main import BaseModel

from app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from app.domain.services.roster_player_service import RosterPlayerService, create_roster_player_service
from app.yards_py.core.annotate_args import annotate_args
from app.yards_py.domain.entities.draft import Draft, DraftSlot


def create_auction_draft_service(
    roster_player_service: RosterPlayerService = Depends(create_roster_player_service),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
):
    return AuctionDraftService(roster_player_service=roster_player_service, league_roster_repo=league_roster_repo)


@annotate_args
class CompleteSlotResult(BaseModel):
    player_assigned: bool
    error: Optional[str]
    draft_complete: bool = False

    @property
    def success(self) -> bool:
        return self.player_assigned


class AuctionDraftService:
    def __init__(self, roster_player_service: RosterPlayerService, league_roster_repo: LeagueRosterRepository):
        self.roster_player_service = roster_player_service
        self.league_roster_repo = league_roster_repo

    def complete_slot(self, league_id: str, draft: Draft, slot: DraftSlot, winner_id: str, transaction: Transaction) -> CompleteSlotResult:
        roster = self.league_roster_repo.get(league_id, winner_id, transaction)
        slot.completed = True
        message = f"{roster.name} selected {slot.player.full_name} for ${slot.bid} (no other players were able to bid)"
        slot.result = message
        draft.draft_events.insert(0, f"Pick #{slot.pick_number} - {message}")

        player_assigned, error = self.roster_player_service.assign_player_to_roster(league_id, roster, slot.player, transaction)

        if not player_assigned:
            return CompleteSlotResult(player_assigned=player_assigned, error=error)

        draft_complete = self.update_next_slot(draft)

        return CompleteSlotResult(player_assigned=player_assigned, draft_complete=draft_complete)

    def update_next_slot(self, draft: Draft) -> bool:
        next_slot = next([slot for slot in draft.slots if not slot.completed], None)

        draft_complete = next_slot is not None
        # TODO: mark rosters ineligible if they are full, eligible if they are not.  marking all rosters means I don't have to undo those
        # TODO: if draft is complete, set that stat on the draft itself, and maybe also update the league object?
        return draft_complete
