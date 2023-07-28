from typing import Dict, List, Optional, Union

from pydantic.main import BaseModel

from app.core.annotate_args import annotate_args
from app.core.base_entity import BaseEntity
from app.domain.entities.league_position import LeaguePosition
from app.domain.entities.league_positions_config import LeaguePositionsConfig
from app.domain.entities.player import Player
from app.domain.entities.roster import Roster
from app.domain.enums.draft_type import DraftType


@annotate_args
class DraftOrder(BaseModel):
    roster_id: str
    budget: int = 100


@annotate_args
class DraftBidder(BaseModel):
    roster_id: str
    index: int = 0
    passed: bool = False
    outbid: bool = False
    in_eligible: bool = False


@annotate_args
class DraftSlot(BaseModel):
    pick_number: int
    roster_id: Optional[str] = None
    player: Optional[Player] = None
    nominator: Optional[str] = None
    bidder_index: Optional[int] = None
    bid: Optional[int] = None
    bidders: Optional[List[DraftBidder]] = None
    result: Optional[str] = None
    completed: bool = False

    def get_next_bidder(self, current_bidder_index) -> Union[DraftBidder, None]:
        if not self.bidders:
            return None

        next_bidder = next((bidder for bidder in self.bidders if self.is_eligible_after_index(current_bidder_index, bidder)), None)

        if not next_bidder:
            next_bidder = next((bidder for bidder in self.bidders if self.is_eligible_after_index(-1, bidder)), None)

        return next_bidder

    def is_eligible_after_index(self, index: int, bidder: DraftBidder) -> bool:
        return (
            bidder.index > index
            and not bidder.outbid
            and not bidder.passed
            and not bidder.roster_id == self.roster_id
            and not bidder.index == self.bidder_index
        )


@annotate_args
class DraftRosterPosition(BaseModel):
    position: LeaguePosition
    player: Optional[Player] = None


@annotate_args
class DraftRoster(BaseModel):
    roster_id: str
    roster_name: str
    budget: int
    positions: Dict[str, DraftRosterPosition] = None


@annotate_args
class Draft(BaseEntity):
    commissioner_id: str
    draft_type: DraftType
    slots: List[DraftSlot]
    draft_order: Optional[Dict[str, DraftOrder]] = None
    is_paused: bool = False
    id: str = "draft"
    draft_events: List[str] = []
    complete: bool = False


def generate_draft(
    commissioner_id: str,
    draft_type: DraftType,
    rosters: List[Roster],
    roster_config: LeaguePositionsConfig,
    draft_order: Optional[List[DraftOrder]],
) -> Draft:
    rounds = roster_config.active_position_count()
    slots_count = len(rosters) * rounds

    # TODO: for snake and auction, assign roster_ids based on order
    slots = []  # type: List[DraftSlot]
    pick_number = 1

    for i in range(0, slots_count):
        slot = DraftSlot(pick_number=pick_number)
        slots.append(slot)
        pick_number += 1

    if draft_type == DraftType.AUCTION:
        for slot in slots:
            next_roster = draft_order.pop(0)
            slot.nominator = next_roster.roster_id
            draft_order.append(next_roster)
            slot.bidders = [DraftBidder(roster_id=roster.roster_id) for roster in draft_order]
            i = 0
            for bidder in slot.bidders:
                bidder.index = i
                i += 1

    if draft_type == DraftType.SNAKE:
        reverse = []
        for slot in slots:
            if not draft_order:
                draft_order = reverse
                reverse = []

            next_roster = draft_order.pop(0)
            slot.roster_id = next_roster.roster_id
            reverse.insert(0, next_roster)

    if draft_order:
        draft_order = {d.roster_id: d for d in draft_order}

    return Draft(commissioner_id=commissioner_id, draft_type=draft_type, slots=slots, draft_order=draft_order)


# def generate_rosters(positions: dict[str, LeaguePosition],):
#     draft_positions = {}

#     for position_key in positions:
#         position = positions[position_key]
#         if position.is_active_position_type():
#             draft_positions[position_key] = DraftRosterPosition(position=position)

#     return draft_positions
