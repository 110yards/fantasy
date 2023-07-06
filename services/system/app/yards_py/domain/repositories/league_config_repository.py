from typing import Optional

from app.yards_py.core.firestore_proxy import FirestoreProxy
from app.yards_py.domain.entities.league import PrivateConfig
from app.yards_py.domain.entities.league_positions_config import LeaguePositionsConfig
from app.yards_py.domain.entities.league_state import LeagueState
from app.yards_py.domain.entities.schedule import Schedule
from app.yards_py.domain.entities.scoring_settings import ScoringSettings
from google.cloud.firestore_v1.transaction import Transaction


def create_league_config_repository():
    firestore = FirestoreProxy(None)
    return LeagueConfigRepository(firestore)


class LeagueConfigRepository:
    path = "league"

    def __init__(self, firestore: FirestoreProxy):
        self.firestore = firestore

    @staticmethod
    def path(league_id):
        return f"league/{league_id}/config"

    def get_private_config(self, league_id, transaction: Transaction = None) -> PrivateConfig:
        config = self.firestore.get(LeagueConfigRepository.path(league_id), "private", transaction)
        return PrivateConfig(**config)

    # def set_private_config(self, league_id, config: PrivateConfig, transaction: Transaction = None) -> PrivateConfig:
    #     return self.firestore.set(LeagueConfigRepository.path(league_id), config, transaction)

    def get_scoring_config(self, league_id, transaction: Transaction = None) -> ScoringSettings:
        config = self.firestore.get(LeagueConfigRepository.path(league_id), "scoring", transaction)
        return ScoringSettings(**config) if config else None

    # def set_scoring_config(self, league_id, config: ScoringSettings, transaction: Transaction = None) -> ScoringSettings:
    #     return self.firestore.set(LeagueConfigRepository.path(league_id), config, transaction)

    def get_positions_config(self, league_id, transaction: Transaction = None) -> LeaguePositionsConfig:
        config = self.firestore.get(LeagueConfigRepository.path(league_id), "positions", transaction)
        return LeaguePositionsConfig(**config)

    # def set_positions_config(self, league_id, config: LeaguePositionsConfig, transaction: Transaction = None) -> LeaguePositionsConfig:
    #     return self.firestore.set(LeagueConfigRepository.path(league_id), config, transaction)

    def get_schedule_config(self, league_id, transaction: Transaction = None) -> Optional[Schedule]:
        config = self.firestore.get(LeagueConfigRepository.path(league_id), "schedule", transaction)
        return Schedule(**config) if config else None

    def set_schedule_config(self, league_id, config: Schedule, transaction: Transaction = None) -> Schedule:
        return self.firestore.set(LeagueConfigRepository.path(league_id), config, transaction)

    def get_state(self, league_id, transaction: Transaction = None) -> LeagueState:
        config = self.firestore.get(LeagueConfigRepository.path(league_id), "state", transaction)
        return LeagueState(**config) if config else LeagueState()

    def set_state(self, league_id, state: LeagueState, transaction: Transaction = None) -> LeagueState:
        return self.firestore.set(LeagueConfigRepository.path(league_id), state, transaction)
