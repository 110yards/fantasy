from typing import Optional

from fastapi import Depends

from app.config.settings import Settings, get_settings
from app.core.rtdb_client import RTDBClient, create_rtdb_client
from app.domain.models.injury_report import InjuryReport


class InjuryReportStore:
    def __init__(self, settings: Settings, rtdb_client: RTDBClient):
        self.settings = settings
        self.rtdb_client = rtdb_client

    def path(self) -> str:
        env = self.settings.environment.lower()
        return f"{env}/injury_report"

    def get_report(self) -> Optional[InjuryReport]:
        path = self.path()
        data = self.rtdb_client.get(path)
        return InjuryReport(**data) if data else None

    def save_report(self, report: InjuryReport) -> None:
        path = self.path()
        self.rtdb_client.set(path, report.dict())


def create_injury_report_store(
    settings: Settings = Depends(get_settings), rtbd_client: RTDBClient = Depends(create_rtdb_client)
) -> InjuryReportStore:
    return InjuryReportStore(
        settings=settings,
        rtdb_client=rtbd_client,
    )
