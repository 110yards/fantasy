from app.core.base_entity import BaseEntity
from app.domain.entities.player import Player


class OwnedPlayer(BaseEntity):
    player_id: str
    owner_id: str

    @staticmethod
    def create(owner_id: str, player: Player):
        return OwnedPlayer(id=player.player_id, player_id=player.player_id, owner_id=owner_id)
