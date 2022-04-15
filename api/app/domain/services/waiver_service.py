

from api.app.domain.entities.league_transaction import LeagueTransaction
from api.app.domain.entities.waiver_bid import WaiverBid, WaiverBidResult
from api.app.domain.entities.roster import Roster
from typing import Dict, List, Optional, Union

from google.cloud.firestore_v1.transaction import Transaction
from fastapi import Depends
from api.app.domain.services.roster_player_service import RosterPlayerService, create_roster_player_service
from copy import deepcopy


def create_waiver_service(roster_player_service: RosterPlayerService = Depends(create_roster_player_service)):
    return WaiverService(roster_player_service)


class WaiverService:
    def __init__(
        self,
        roster_player_service: RosterPlayerService,
    ):
        self.roster_player_service = roster_player_service

    def get_initial_waiver_priority(self, rosters: List[Roster]) -> List[str]:
        waiver_priority = deepcopy(rosters)
        waiver_priority.sort(key=lambda x: x.rank, reverse=True)

        return [roster.id for roster in waiver_priority]

    def process_bids(self, rosters: Union[List[Roster], Dict[str, Roster]]) -> List[WaiverBid]:
        waiver_priority = self.get_initial_waiver_priority(rosters)

        all_bids: List[WaiverBid] = []
        for roster in rosters:
            if roster.waiver_bids:
                all_bids.extend(roster.waiver_bids)

        all_bids.sort(key=lambda x: x.amount, reverse=True)

        if isinstance(rosters, List):
            rosters = {roster.id: roster for roster in rosters}

        dropped_players_for_roster = {roster.id: [] for roster in rosters.values()}

        for bid in all_bids:
            roster = rosters[bid.roster_id]
            if bid.result != WaiverBidResult.Unprocessed:
                continue

            if bid.amount > rosters[bid.roster_id].waiver_budget:
                bid.result = WaiverBidResult.FailedNotEnoughMoney
                continue

            if bid.drop_player:
                on_roster = roster.find_player_position(bid.drop_player.id) is not None
                if not on_roster:
                    bid.result = WaiverBidResult.FailedDropPlayerNotOnRoster
                    continue

                already_dropped = bid.drop_player.id in dropped_players_for_roster[bid.roster_id]
                if already_dropped:
                    bid.result = WaiverBidResult.FailedDropPlayerNotOnRoster
                    continue

            if not bid.drop_player:
                has_space = self.roster_player_service.find_position_for(bid.player, rosters[bid.roster_id])

                if not has_space:
                    bid.result = WaiverBidResult.FailedNoRosterSpace
                    continue

            other_bids = [x for x in all_bids if x != bid and x.player.id == bid.player.id]
            tie_bids = [x for x in other_bids if x.amount == bid.amount]
            losing_bids = [x for x in other_bids if x.amount < bid.amount]

            for losing_bid in losing_bids:
                losing_bid.result = WaiverBidResult.FailedOutBid

            if not tie_bids:
                self.record_winning_bid(bid, rosters, waiver_priority, dropped_players_for_roster)

            else:
                tie_bids.append(bid)

                winner_priority = 99
                winner_id = ""
                for tie_bid in tie_bids:
                    priority = waiver_priority.index(tie_bid.roster_id)
                    if priority < winner_priority:
                        winner_id = tie_bid.roster_id
                        winner_priority = priority

                for tie_bid in tie_bids:
                    if tie_bid.roster_id == winner_id:
                        self.record_winning_bid(tie_bid, rosters, waiver_priority, dropped_players_for_roster)
                    else:
                        tie_bid.result = WaiverBidResult.FailedLowerPriority

        return all_bids

    def record_winning_bid(
        self,
        winning_bid: WaiverBid,
        rosters: Dict[str, Roster],
        waiver_priority: List[str],
        dropped_players_for_roster: Dict[str, List[str]],
    ):
        winning_bid.result = WaiverBidResult.SuccessPending

        index = waiver_priority.index(winning_bid.roster_id)
        waiver_priority.pop(index)
        waiver_priority.append(winning_bid.roster_id)

        rosters[winning_bid.roster_id].waiver_budget -= winning_bid.amount

        if winning_bid.drop_player:
            dropped_players_for_roster[winning_bid.roster_id].append(winning_bid.drop_player.id)

    def apply_winning_bid(self, league_id: str, bid: WaiverBid, roster: Roster, transaction: Transaction) -> Optional[List[LeagueTransaction]]:
        if bid.drop_player:
            target_position = roster.find_player_position(bid.drop_player.id)
        else:
            target_position = self.roster_player_service.find_position_for(bid.player, roster)

        if not target_position:
            bid.result = WaiverBidResult.FailedNoRosterSpace
        else:
            success, trx_or_error = self.roster_player_service.assign_player_to_roster(league_id, roster, bid.player, transaction,
                                                                                       target_position=target_position, record_transaction=True,
                                                                                       waiver_bid=bid.amount)

            if success:
                bid.result = WaiverBidResult.Success
                return trx_or_error
            else:
                bid.result = WaiverBidResult.FailedNoRosterSpace
