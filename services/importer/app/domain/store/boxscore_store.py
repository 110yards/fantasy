from fastapi import Depends

from app.config.settings import Settings, get_settings
from app.core.rtdb_client import RTDBClient, create_rtdb_client
from app.domain.models.game import Game


class BoxscoreStore:
    def __init__(self, settings: Settings, rtdb_client: RTDBClient):
        self.settings = settings
        self.rtdb_client = rtdb_client

    def path(self, year: int, game_id: str) -> str:
        return f"{self.settings.environment.lower()}/boxscores/{year}/{game_id}"

    def get_boxscore(self, year: int, game_id: str) -> Game | None:
        game = self.rtdb_client.get(self.path(year, game_id))
        game = Game(**game) if game else None

    def save_boxscore(self, year: int, game: Game) -> None:
        path = self.path(year, game.game_id)
        self.rtdb_client.set(path, game.dict())


def create_boxscore_store(
    settings: Settings = Depends(get_settings), rtdb_client: RTDBClient = Depends(create_rtdb_client)
) -> BoxscoreStore:
    return BoxscoreStore(settings=settings, rtdb_client=rtdb_client)
