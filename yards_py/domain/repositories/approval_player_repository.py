

from google.cloud.firestore_v1.transaction import Transaction
from yards_py.core.firestore_proxy import FirestoreProxy
from yards_py.domain.entities.player import Player



class ApprovalPlayerRepository():
    def __init__(self, firestore: FirestoreProxy[Player]):
        self.firestore = firestore

    @staticmethod
    def path():
        return "mod/approvals/players"
    
    def get(self, player_id: str, transaction: Transaction = None) -> Player:
        return self.firestore.get(ApprovalPlayerRepository.path(), player_id, transaction)

    def delete(self, player_id: str, transaction: Transaction = None):
        self.firestore.delete(ApprovalPlayerRepository.path(), player_id, transaction)

    
    def set_all(self, players: list[Player]) -> None:
        self.firestore.set_all(ApprovalPlayerRepository.path(), players)
        

def create_approval_player_repository():
    firestore = FirestoreProxy[Player](Player.parse_obj)
    return ApprovalPlayerRepository(firestore)
