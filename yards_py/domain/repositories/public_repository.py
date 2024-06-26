from ..entities.season_schedule import SeasonSchedule
from ..entities.schedule import Schedule
from yards_py.domain.entities.state import State
from yards_py.domain.entities.scoreboard import Scoreboard
from yards_py.domain.entities.opponents import Opponents
from yards_py.domain.entities.switches import Switches
from yards_py.domain.entities.scoring_info import ScoringInfo
from yards_py.core.firestore_proxy import FirestoreProxy
from google.cloud.firestore_v1.transaction import Transaction
from yards_py.domain.entities.league import PrivateConfig


def create_public_repository():
    firestore = FirestoreProxy(None)
    return PublicRepository(firestore)


class PublicRepository:
    path = "public"

    def __init__(self, firestore: FirestoreProxy):
        self.firestore = firestore

    def set_scoring_info(self, info: ScoringInfo, transaction: Transaction = None) -> PrivateConfig:
        return self.firestore.set(self.path, info, transaction)

    def get_switches(self, transaction: Transaction = None) -> Switches:
        switches = self.firestore.get(self.path, "switches", transaction)
        return Switches.parse_obj(switches)

    def set_switches(self, switches: Switches, transaction: Transaction = None):
        self.firestore.set(self.path, switches, transaction)

    def get_opponents(self, transaction: Transaction = None) -> Opponents:
        opponents = self.firestore.get(self.path, "opponents", transaction)
        return Opponents.parse_obj(opponents)

    def set_opponents(self, opponents: Opponents, transaction: Transaction = None):
        self.firestore.set(self.path, opponents, transaction)

    def get_scoreboard(self, transaction: Transaction = None) -> Scoreboard:
        scoreboard = self.firestore.get(self.path, "scoreboard", transaction)
        return Scoreboard.parse_obj(scoreboard) if scoreboard else None

    def set_scoreboard(self, scoreboard: Scoreboard, transaction: Transaction = None):
        self.firestore.set(self.path, scoreboard, transaction)

    def get_state(self, transaction: Transaction = None) -> State:
        state = self.firestore.get(self.path, "state", transaction)
        return State.parse_obj(state)

    def set_state(self, state: State, transaction: Transaction = None):
        self.firestore.set(self.path, state, transaction)

    def get_schedule(self, transaction: Transaction = None) -> SeasonSchedule:
        schedule = self.firestore.get(self.path, "schedule", transaction)
        return SeasonSchedule(**schedule) if schedule else SeasonSchedule()
    
    def set_schedule(self, schedule: SeasonSchedule, transaction: Transaction = None):
        self.firestore.set(self.path, schedule, transaction)
        
