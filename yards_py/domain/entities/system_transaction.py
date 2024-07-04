from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from .player import Player

from ...core.base_entity import BaseEntity



class TransactionType(str, Enum):
    add_player = "add_player"
    match_player = "match_player"
    update_player_game = "update_player_game"
    revert_player_game = "revert_player_game"


class SystemTransaction(BaseEntity):
    user_id: str
    message: str
    timestamp: datetime
    transaction_type: TransactionType

    @staticmethod
    def add_player(user_id: str, player: Player) -> SystemTransaction:
        message = f"{player.display_name} was added to the system."
        trx_type = TransactionType.add_player

        return SystemTransaction(user_id=user_id, message=message, timestamp=datetime.now(tz=timezone.utc), transaction_type=trx_type)

    @staticmethod
    def match_player(user_id: str, updated_player: Player, original_player: Player) -> SystemTransaction:
        message = f"{updated_player.display_name} ({updated_player.player_id}) was matched to {original_player.display_name} ({original_player.player_id})."
        trx_type = TransactionType.match_player

        return SystemTransaction(user_id=user_id, message=message, timestamp=datetime.now(tz=timezone.utc), transaction_type=trx_type)

    @staticmethod
    def update_player_game(user_id: str, updated_player: Player, game_id: int) -> SystemTransaction:        
        message = f"{updated_player.display_name} ({updated_player.player_id}) was updated for game {game_id}."
        trx_type = TransactionType.update_player_game

        return SystemTransaction(user_id=user_id, message=message, timestamp=datetime.now(tz=timezone.utc), transaction_type=trx_type)

    @staticmethod
    def revert_player_game(user_id: str, updated_player: Player, game_id: int) -> SystemTransaction:        
        message = f"{updated_player.display_name} ({updated_player.player_id}) was reverted for game {game_id}."
        trx_type = TransactionType.revert_player_game

        return SystemTransaction(user_id=user_id, message=message, timestamp=datetime.now(tz=timezone.utc), transaction_type=trx_type)
