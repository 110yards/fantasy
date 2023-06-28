from datetime import datetime
from typing import Optional

from dateutil import parser
from fastapi import Depends

from ...yards_py.core.rtdb_client import RTDBClient, create_rtdb_client


class ImportStateStore:
    def __init__(self, rtdb_client: RTDBClient):
        self.rtdb_client = rtdb_client

    def get_last_player_update(self) -> Optional[datetime]:
        path = "import_state/last_player_update"
        data = self.rtdb_client.get(path)
        return parser.isoparse(data) if data else None


def create_import_state_store(rtbd_client: RTDBClient = Depends(create_rtdb_client)) -> ImportStateStore:
    return ImportStateStore(
        rtdb_client=rtbd_client,
    )
