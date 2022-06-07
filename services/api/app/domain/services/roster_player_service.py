

from services.api.app.domain.enums.position_type import PositionType
from yards_py.domain.entities.league_transaction import LeagueTransaction
from services.api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from services.api.app.domain.repositories.league_transaction_repository import LeagueTransactionRepository, create_league_transaction_repository
from services.api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from yards_py.domain.entities.roster import Roster
from typing import List, Optional, Tuple, Union

from yards_py.domain.entities.league_position import LeaguePosition
from yards_py.domain.entities.owned_player import OwnedPlayer
from yards_py.domain.entities.player import Player
from services.api.app.domain.repositories.league_owned_player_repository import (
    LeagueOwnedPlayerRepository, create_league_owned_player_repository)
from fastapi.param_functions import Depends
from google.cloud.firestore_v1.transaction import Transaction


def create_roster_player_service(
    league_owned_player_repo: LeagueOwnedPlayerRepository = Depends(create_league_owned_player_repository),
    roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    league_transaction_repo: LeagueTransactionRepository = Depends(create_league_transaction_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
):
    return RosterPlayerService(
        league_owned_player_repo,
        roster_repo=roster_repo,
        league_transaction_repo=league_transaction_repo,
        league_config_repo=league_config_repo
    )


class RosterPlayerService:
    def __init__(
        self,
        league_owned_player_repo: LeagueOwnedPlayerRepository,
        roster_repo: LeagueRosterRepository,
        league_transaction_repo: LeagueTransactionRepository,
        league_config_repo: LeagueConfigRepository,
    ):
        self.league_owned_player_repo = league_owned_player_repo
        self.roster_repo = roster_repo
        self.league_transaction_repo = league_transaction_repo
        self.league_config_repo = league_config_repo

    def find_position_for(self, player: Player, roster: Roster) -> Optional[LeaguePosition]:

        positions = list(roster.positions.values())

        def sort_key(item: LeaguePosition):
            adjustment = 0
            # prioritize all 3 flex positions after natural positions to avoid impossible draft situations
            # prioritize flex after more specific flex positions too
            if item.position_type in (PositionType.o_flex, PositionType.d_flex):
                adjustment = 1000
            elif item.position_type == PositionType.flex:
                adjustment = 2000

            # finally, prioritize bench last
            if item.position_type == PositionType.bench:
                adjustment = 10000

            return adjustment + item.id

        positions.sort(key=sort_key)

        # ensure there is a starting position for this player, even if it's occupied currently
        eligible_starting_positions = [p for p in positions if p.is_starting_position_type() and p.position_type.is_eligible_for(player.position)]

        if not eligible_starting_positions:
            return None

        for position in positions:
            if not position.position_type.is_active_position_type():
                continue

            if position.player:
                continue

            if position.position_type.is_eligible_for(player.position):
                return position

    def assign_player_to_roster(
        self,
        league_id: str,
        roster: Roster,
        player: Player,
        transaction: Transaction = None,
        target_position: LeaguePosition = None,
        record_transaction: bool = False,
        waiver_bid: int = None
    ) -> Tuple[bool, Union[str, List[LeagueTransaction]]]:
        config = self.league_config_repo.get_positions_config(league_id)
        if not config:
            return False, "League position config not found"

        position = target_position or self.find_position_for(player, roster)

        if not position:
            return False, "Unable to find position for player"

        if not config.allow_bench_qb:
            if player.position == PositionType.qb and roster.count_qbs() == 1 and not self.dropping(PositionType.qb, target_position):
                return False, "Rosters are limited to 1 quarterback"

        if not config.allow_bench_rb:
            if player.position == PositionType.rb and roster.count_rbs() == 1 and not self.dropping(PositionType.rb, target_position):
                return False, "Rosters are limited to 1 running back"

        if not config.allow_bench_k:
            if player.position == PositionType.k and roster.count_kickers() == 1 and not self.dropping(PositionType.k, target_position):
                return False, "Rosters are limited to 1 kicker"

        league_transactions = self.assign_player_to_roster_position(
            league_id, roster, player, position, transaction, record_transaction=record_transaction, waiver_bid=waiver_bid)

        return True, league_transactions

    def dropping(self, type: PositionType, target_position: LeaguePosition) -> bool:
        return target_position and target_position.player and target_position.player.position == type

    def assign_player_to_roster_position(
            self,
            league_id: str,
            roster: Roster,
            player: Player,
            position: LeaguePosition,
            transaction: Transaction = None,
            record_transaction: bool = False,
            waiver_bid: int = None,
    ) -> Optional[List[LeagueTransaction]]:
        drop_player: Player = None
        if position.player:
            drop_player = position.player
            self.league_owned_player_repo.delete(league_id, drop_player.id, transaction)

        position.player = player
        owned_player = OwnedPlayer.create(roster.id, player)
        roster.active_player_count += 1

        self.league_owned_player_repo.set(league_id, owned_player, transaction)
        self.roster_repo.set(league_id, roster, transaction)

        league_transactions = []

        if record_transaction:
            if drop_player:
                drop_transaction = LeagueTransaction.drop_transaction(league_id, roster, drop_player)
                self.league_transaction_repo.create(league_id, drop_transaction, transaction)
                league_transactions.append(drop_transaction)

            if waiver_bid is not None:
                add_transaction = LeagueTransaction.waiver_claim_transaction(league_id, roster, player, waiver_bid)
            else:
                add_transaction = LeagueTransaction.add_transaction(league_id, roster, player)
            self.league_transaction_repo.create(league_id, add_transaction, transaction)
            league_transactions.append(add_transaction)

        return league_transactions

    def remove_player_from_roster(
        self,
        league_id: str,
        roster: Roster,
        player_id: str,
        transaction: Transaction = None
    ):

        for position_id in roster.positions:
            position = roster.positions[position_id]
            if not position.player or position.player.id != player_id:
                continue

            position.player = None

        active_filled_positions = [position for position in roster.positions.values() if position.player and position.position_type.is_active_position_type()]
        roster.active_player_count = len(active_filled_positions)

        self.league_owned_player_repo.delete(league_id, player_id, transaction)
        self.roster_repo.set(league_id, roster, transaction)
