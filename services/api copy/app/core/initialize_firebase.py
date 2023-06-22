import firebase_admin
from firebase_admin import App, credentials

from app.config.settings import Settings


def initialize_firebase(settings: Settings) -> App:
    cred = credentials.ApplicationDefault()

    return firebase_admin.initialize_app(
        credential=cred,
        options={"databaseURL": settings.rtdb_url},
    )
