from yards_py.core.base_entity import BaseEntity
from yards_py.core.annotate_args import annotate_args
from yards_py.domain.entities.player import Player


@annotate_args
class OwnedPlayer(BaseEntity):
    player_id: str
    owner_id: str

    @staticmethod
    def create(owner_id: str, player: Player):
        return OwnedPlayer(id=player.id, player_id=player.id, owner_id=owner_id)
