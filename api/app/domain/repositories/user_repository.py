from typing import Dict
from api.app.core.firestore_proxy import FirestoreProxy, Query
from api.app.domain.entities.user import User
from google.cloud.firestore_v1.transaction import Transaction


def create_user_repository():
    firestore = FirestoreProxy[User](User.parse_obj)
    return UserRepository(firestore)


class UserRepository:
    path = "user"

    def __init__(self, firestore: FirestoreProxy[User]):
        self.firestore = firestore

    def get(self, user_id, transaction: Transaction = None) -> User:
        return self.firestore.get(self.path, user_id, transaction)

    def get_by_email(self, email: str) -> User:
        query = Query("email", "==", email)
        results = self.firestore.where(self.path, query)

        if len(results) == 1:
            return results[0]
        else:
            return None

    def create(self, user: User, transaction: Transaction = None) -> User:
        return self.firestore.create(self.path, user, transaction)

    def update(self, user: User, transaction: Transaction = None) -> User:
        return self.firestore.update(self.path, user, transaction)

    def partial_update(self, user_id: str, updates: Dict, transaction: Transaction = None) -> User:
        return self.firestore.partial_update(self.path, user_id, updates, transaction)
