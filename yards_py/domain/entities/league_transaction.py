from __future__ import annotations

from enum import Enum
from typing import Optional
from yards_py.domain.entities.roster import Roster
from yards_py.domain.entities.player import Player
from yards_py.core.base_entity import BaseEntity
from datetime import datetime, timezone
from yards_py.core.annotate_args import annotate_args


class TransactionType(str, Enum):
    ADD_PLAYER = "add_player"
    CLAIM_PLAYER = "claim_player"
    DROP_PLAYER = "drop_player"
    CHANGE_ROSTER_NAME = "change_roster_name"
    COMMISSIONER_DROP_PLAYER = "commissioner_drop_player"
    COMMISSIONER_CHANGE_ROSTER_NAME = "commissioner_change_roster_name"
    COMMISSIONER_CHANGE_SCORING = "commissioner_change_scoring"
    COMMISSIONER_MOVE_PLAYER = "commissioner_move_player"
    LEAGUE_EVENT = "league_event"
    COMMISSIONER_CHANGE_WAIVER_BUDGET = "commissioner_change_waiver_budget"
    COMMISSIONER_TRANSFER_ROSTER_OWNERSHIP = "commissioner_transfer_roster_ownership"
    COMMISSIONER_ADJUST_RESULT = "commissioner_adjust_result"


@annotate_args
class LeagueTransaction(BaseEntity):
    type: TransactionType
    league_id: str
    roster_id: Optional[str]
    player_id: Optional[str]
    message: str
    timestamp: datetime

    @staticmethod
    def drop_transaction(league_id: str, roster: Roster, player: Player, is_commissioner_override: bool = False):
        if is_commissioner_override:
            message = f"Commissioner dropped {player.display_name} for {roster.name}"
            trx_type = TransactionType.COMMISSIONER_DROP_PLAYER
        else:
            message = f"{roster.name} dropped {player.display_name}"
            trx_type = TransactionType.DROP_PLAYER

        return LeagueTransaction(timestamp=datetime.now(timezone.utc),
                                 league_id=league_id, roster_id=roster.id, player_id=player.id, message=message, type=trx_type)

    @staticmethod
    def add_transaction(league_id: str, roster: Roster, player: Player):
        message = f"{roster.name} added {player.display_name}"
        return LeagueTransaction(timestamp=datetime.now(timezone.utc),
                                 league_id=league_id, roster_id=roster.id, player_id=player.id, message=message, type=TransactionType.ADD_PLAYER)

    @staticmethod
    def waiver_claim_transaction(league_id: str, roster: Roster, player: Player, bid: int):
        message = f"{roster.name} claimed {player.display_name} on waivers (${bid})"
        return LeagueTransaction(timestamp=datetime.now(timezone.utc),
                                 league_id=league_id, roster_id=roster.id, player_id=player.id, message=message, type=TransactionType.CLAIM_PLAYER)

    @staticmethod
    def change_roster_name(league_id: str, roster_id: str, new_name: str, old_name: str, commissioner_change: bool):
        if commissioner_change:
            message = f"Commissioner changed {old_name} to {new_name}"
            trx_type = TransactionType.COMMISSIONER_CHANGE_ROSTER_NAME
        else:
            message = f"{old_name} changed name to {new_name}"
            trx_type = TransactionType.CHANGE_ROSTER_NAME

        return LeagueTransaction(timestamp=datetime.now(timezone.utc),
                                 league_id=league_id, roster_id=roster_id, message=message, type=trx_type)

    @staticmethod
    def change_scoring(league_id: str):
        message = "Commissioner changed the league scoring settings"
        return LeagueTransaction(timestamp=datetime.now(timezone.utc),
                                 league_id=league_id, message=message, type=TransactionType.COMMISSIONER_CHANGE_SCORING)

    @staticmethod
    def commissioner_move_player(league_id: str, roster: Roster, player: Player, from_position: str, to_position: str):
        message = f"Commissioner moved {player.display_name} on {roster.name} from {from_position} to {to_position}"
        return LeagueTransaction(timestamp=datetime.now(timezone.utc), league_id=league_id, roster_id=roster.id, player_id=player.id,
                                 message=message, type=TransactionType.COMMISSIONER_MOVE_PLAYER)

    @staticmethod
    def league_event(league_id: str, message: str) -> LeagueTransaction:
        return LeagueTransaction(timestamp=datetime.now(timezone.utc), league_id=league_id, message=message, type=TransactionType.LEAGUE_EVENT)

    @staticmethod
    def change_waiver_budget(league_id: str, roster_id: str, roster_name: str, new_value: int, old_value: int):
        message = f"Commissioner changed the waiver budget for {roster_name} from ${old_value} to ${new_value}"
        trx_type = TransactionType.COMMISSIONER_CHANGE_ROSTER_NAME

        return LeagueTransaction(timestamp=datetime.now(timezone.utc),
                                 league_id=league_id, roster_id=roster_id, message=message, type=trx_type)

    @staticmethod
    def transfer_roster_ownership(league_id: str, roster_id: str, roster_name: str, new_owner_email: str):
        message = f"Commissioner transferred {roster_name} to {new_owner_email}"
        trx_type = TransactionType.COMMISSIONER_TRANSFER_ROSTER_OWNERSHIP

        return LeagueTransaction(timestamp=datetime.now(timezone.utc),
                                 league_id=league_id, roster_id=roster_id, message=message, type=trx_type)

    @staticmethod
    def commissioner_adjust_result(league_id: str, week_number: int, away_name: str, home_name: str, away_adjustment: int, home_adjustment: int):

        home_adjustment = f"{home_adjustment:+}"
        away_adjustment = f"{away_adjustment:+}"

        message = f"Commissioner adjusted the result of the week {week_number} matchup between {away_name} ({away_adjustment}) and {home_name} ({home_adjustment})."

        return LeagueTransaction(
                league_id=league_id,
                type=TransactionType.COMMISSIONER_ADJUST_RESULT,
                timestamp=datetime.now(timezone.utc),
                message=message
            )
