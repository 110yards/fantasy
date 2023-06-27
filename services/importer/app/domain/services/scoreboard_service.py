import requests
from dateutil import parser
from fastapi import Depends

from ...config.settings import Settings, get_settings
from ..models.scoreboard import Locks, Opponents, Scoreboard, ScoreboardGame
from ..store.state_store import StateStore, create_state_store


class ScoreboardService:
    def __init__(self, settings: Settings, state_store: StateStore):
        self.settings = settings
        self.state_store = state_store

    def get_scoreboard(self) -> Scoreboard:
        state = self.state_store.get_state()
        current_week = state.current_week

        data = requests.get(self.settings.realtime_schedule_url).json()

        return load_scoreboard(data, current_week)


def load_scoreboard(data: dict, current_week: int) -> Scoreboard:
    games = map_games(data, current_week)
    locks = create_locks(games)
    opponents = create_opponents(games)

    return Scoreboard(
        games=games,
        locks=locks,
        opponents=opponents,
    )


def map_games(data: dict, current_week: int) -> list[ScoreboardGame]:
    games = []

    for week in data:
        if week["type"] == "REG" and week["number"] == current_week:
            games.extend(map_week_games(week["tournaments"]))

    return games


def map_week_games(week_data: dict) -> list[ScoreboardGame]:
    games = []
    for game_data in week_data:
        games.append(map_game(game_data))

    return games


def map_game(game_data: dict) -> ScoreboardGame:
    game_date = parser.isoparse(game_data["date"])

    return ScoreboardGame(
        game_date=game_date,
        away_abbr=game_data["awaySquad"]["shortName"],
        home_abbr=game_data["homeSquad"]["shortName"],
        away_score=game_data["awaySquad"]["score"],
        home_score=game_data["homeSquad"]["score"],
        status=game_data["status"],
        quarter=game_data["activePeriod"],
        clock=game_data["clock"],
    )


def create_locks(games: list[ScoreboardGame]) -> Locks:
    started_statuses = ["first_quarter", "second_quarter", "third_quarter", "fourth_quarter", "overtime", "complete"]
    lock_data = {}

    locked_count = 0

    for game in games:
        if game.status in started_statuses:
            locked_count += 1
            lock_data[game.away_abbr] = True
            lock_data[game.home_abbr] = True

    all_locked = locked_count == len(games)

    return Locks.all_locked() if all_locked else Locks(**lock_data)


def create_opponents(games: list[ScoreboardGame]) -> Opponents:
    opponent_data = {}

    for game in games:
        opponent_data[game.away_abbr] = game.home_abbr
        opponent_data[game.home_abbr] = game.away_abbr

    return Opponents(**opponent_data)


def create_scoreboard_service(
    settings: Settings = Depends(get_settings),
    state_store: StateStore = Depends(create_state_store),
) -> ScoreboardService:
    return ScoreboardService(
        settings=settings,
        state_store=state_store,
    )
