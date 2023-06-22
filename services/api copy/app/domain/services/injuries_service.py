from fastapi import Depends

from app.config.settings import Settings, get_settings
from app.core.rtdb_client import RTDBClient, create_rtdb_client
from app.domain.api_response import ApiResponse


class InjuriesService:
    def __init__(self, settings: Settings, rtdb_client: RTDBClient):
        self.settings = settings
        self.rtdb_client = rtdb_client

    def get_injuries(self) -> ApiResponse:
        env = self.settings.environment.lower()
        path = f"{env}/injury_report/reports"

        injuries = self.rtdb_client.get(path)

        return ApiResponse(data=injuries)


def create_injuries_service(
    settings: Settings = Depends(get_settings),
    rtdb_client: RTDBClient = Depends(create_rtdb_client),
):
    return InjuriesService(
        settings=settings,
        rtdb_client=rtdb_client,
    )
