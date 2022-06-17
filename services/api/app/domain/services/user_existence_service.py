

from firebase_admin import auth
from pydantic.main import BaseModel


def create_user_existence_service():
    return UserExistenceService()


class UserExistenceRequest(BaseModel):
    email: str


class UserExistenceService():
    def __init__(self):
        pass

    def does_user_exist(self, email: str):
        if not email:
            return False

        try:
            user = auth.get_user_by_email(email)
            return user is not None
        except auth.UserNotFoundError:
            return False
        except ValueError:
            return False
