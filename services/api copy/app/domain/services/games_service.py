from fastapi import Depends

from app.config.settings import Settings, get_settings
from app.core.rtdb_client import RTDBClient, create_rtdb_client
from app.domain.api_response import ApiResponse


class GamesService:
    def __init__(self, settings: Settings, rtdb_client: RTDBClient):
        self.settings = settings
        self.rtdb_client = rtdb_client

    def get_games(self, year: int) -> ApiResponse:
        env = self.settings.environment.lower()
        path = f"{env}/schedule/{year}/games"

        games = self.rtdb_client.get(path)
        games = [game for game in games.values()]

        return ApiResponse(data=games)

    def get_game(self, year: int, game_id: str) -> ApiResponse:
        env = self.settings.environment.lower()
        path = f"{env}/boxscores/{year}/{game_id}"

        game = self.rtdb_client.get(path)

        if not game:
            path = f"{env}/schedule/{year}/games/{game_id}"
            game = self.rtdb_client.get(path)

        return ApiResponse(data=[game])  # TODO: single game shouldn't be an array, this is a CFL artifact


def create_games_service(
    settings: Settings = Depends(get_settings),
    rtdb_client: RTDBClient = Depends(create_rtdb_client),
) -> GamesService:
    return GamesService(settings=settings, rtdb_client=rtdb_client)
