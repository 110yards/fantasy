from fastapi import Depends

from ...core.rtdb_client import RTDBClient, create_rtdb_client
from ..entities.boxscore import Boxscore


class BoxscoreStore:
    def __init__(self, rtdb_client: RTDBClient):
        self.rtdb_client = rtdb_client

    def path(self, year: int, game_id: str) -> str:
        return f"boxscores/{year}/{game_id}"

    def get_boxscore(self, year: int, game_id: str) -> Boxscore | None:
        game = self.rtdb_client.get(self.path(year, game_id))
        game = Boxscore(**game) if game else None
        return game


def create_boxscore_store(rtdb_client: RTDBClient = Depends(create_rtdb_client)) -> BoxscoreStore:
    return BoxscoreStore(rtdb_client=rtdb_client)
