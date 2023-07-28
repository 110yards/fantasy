from app.core.firestore_proxy import FirestoreProxy
from app.domain.entities.user_roles import UserRoles
from google.cloud.firestore_v1.transaction import Transaction


def create_user_roles_repository():
    firestore = FirestoreProxy[UserRoles](UserRoles.parse_obj)
    return UserRolesRepository(firestore)


class UserRolesRepository:
    path = "user_roles"

    def __init__(self, firestore: FirestoreProxy[UserRoles]):
        self.firestore = firestore

    def get(self, user_id, transaction: Transaction = None) -> UserRoles:
        return self.firestore.get(self.path, user_id, transaction)
