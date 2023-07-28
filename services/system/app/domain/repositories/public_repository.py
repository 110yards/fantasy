from app.core.firestore_proxy import FirestoreProxy
from app.domain.entities.state import State
from app.domain.entities.switches import Switches
from google.cloud.firestore_v1.transaction import Transaction

from ..entities.scoreboard import Scoreboard


def create_public_repository():
    firestore = FirestoreProxy(None)
    return PublicRepository(firestore)


class PublicRepository:
    path = "public"

    def __init__(self, firestore: FirestoreProxy):
        self.firestore = firestore

    # def set_scoring_info(self, info: ScoringInfo, transaction: Transaction = None) -> PrivateConfig:
    #     return self.firestore.set(self.path, info, transaction)

    def get_switches(self, transaction: Transaction = None) -> Switches:
        switches = self.firestore.get(self.path, "switches", transaction)
        return Switches(**switches)

    # def set_switches(self, switches: Switches, transaction: Transaction = None):
    #     self.firestore.set(self.path, switches, transaction)

    # def get_opponents(self, transaction: Transaction = None) -> Opponents:
    #     opponents = self.firestore.get(self.path, "opponents", transaction)
    #     return Opponents.parse_obj(opponents)

    # def set_opponents(self, opponents: Opponents, transaction: Transaction = None):
    #     self.firestore.set(self.path, opponents, transaction)

    def get_scoreboard(self, transaction: Transaction = None) -> Scoreboard:
        scoreboard = self.firestore.get(self.path, "scoreboard", transaction)
        return Scoreboard(**scoreboard) if scoreboard else None

    # def set_scoreboard(self, scoreboard: Scoreboard, transaction: Transaction = None):
    #     self.firestore.set(self.path, scoreboard, transaction)

    def get_state(self, transaction: Transaction = None) -> State:
        state = self.firestore.get(self.path, "state", transaction)
        return State(**state)

    def set_state(self, state: State, transaction: Transaction = None):
        self.firestore.set(self.path, state, transaction)
