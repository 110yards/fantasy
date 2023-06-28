from fastapi import Depends

from app.config.settings import Settings, get_settings

from ...core.rtdb_client import RTDBClient, create_rtdb_client


class ImportStateStore:
    def __init__(self, settings: Settings, rtdb_client: RTDBClient):
        self.settings = settings
        self.rtdb_client = rtdb_client


def create_import_state_store(
    settings: Settings = Depends(get_settings),
    rtdb_client: RTDBClient = Depends(create_rtdb_client),
) -> ImportStateStore:
    return ImportStateStore(
        settings=settings,
        rtdb_client=rtdb_client,
    )
