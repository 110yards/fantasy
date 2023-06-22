from typing import Any, Dict, Optional

from firebase_admin import db


def create_rtdb_client():
    return RTDBClient()


class RTDBClient:
    def get(self, path: str) -> Optional[tuple | Any]:
        ref = db.reference(path)
        document = ref.get()
        return document

    def set(self, path: str, data: Dict):
        ref = db.reference(path)
        ref.set(data)
