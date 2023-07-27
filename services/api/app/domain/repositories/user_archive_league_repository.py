from typing import Dict, List

from google.cloud.firestore_v1.transaction import Transaction

from app.domain.repositories.user_repository import UserRepository
from app.yards_py.core.firestore_proxy import FirestoreProxy
from app.yards_py.domain.entities.user_league_preview import UserLeaguePreview


def create_user_archive_league_repository():
    firestore = FirestoreProxy[UserLeaguePreview](UserLeaguePreview.parse_obj)
    return UserArchiveLeagueRepository(firestore)


class UserArchiveLeagueRepository:
    def __init__(self, firestore: FirestoreProxy[UserLeaguePreview]):
        self.client = firestore

    @staticmethod
    def path(user_id):
        return f"{UserRepository.path}/{user_id}/archive_league"

    def get_leagues(self, user_id) -> List[UserLeaguePreview]:
        return self.client.get_all(UserArchiveLeagueRepository.path(user_id))

    def set(self, user_id, league: UserLeaguePreview, transaction: Transaction = None):
        return self.client.set(UserArchiveLeagueRepository.path(user_id), league, transaction)

    def get(self, user_id, league_id, transaction: Transaction = None) -> UserLeaguePreview:
        return self.client.get(UserArchiveLeagueRepository.path(user_id), league_id, transaction)

    def delete(self, user_id, league_id, transaction: Transaction = None):
        self.client.delete(UserArchiveLeagueRepository.path(user_id), league_id, transaction)

    def partial_update(self, user_id: str, league_id: str, updates: Dict, transaction: Transaction = None):
        self.client.partial_update(UserArchiveLeagueRepository.path(user_id), league_id, updates, transaction)
