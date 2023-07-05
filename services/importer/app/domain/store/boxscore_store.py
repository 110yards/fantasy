from fastapi import Depends

from app.core.rtdb_client import RTDBClient, create_rtdb_client
from app.domain.models.boxscore import Boxscore


class BoxscoreStore:
    def __init__(self, rtdb_client: RTDBClient):
        self.rtdb_client = rtdb_client

    def path(self, year: int, game_id: str) -> str:
        return f"boxscores/{year}/{game_id}"

    def get_boxscore(self, year: int, game_id: str) -> Boxscore | None:
        game = self.rtdb_client.get(self.path(year, game_id))
        game = Boxscore(**game) if game else None
        return game

    def save_boxscore(self, year: int, box: Boxscore) -> None:
        path = self.path(year, box.game_id)
        self.rtdb_client.set(path, box.model_dump())


def create_boxscore_store(rtdb_client: RTDBClient = Depends(create_rtdb_client)) -> BoxscoreStore:
    return BoxscoreStore(rtdb_client=rtdb_client)
