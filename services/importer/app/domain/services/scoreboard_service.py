from typing import Optional

import requests
from fastapi import Depends

from ...config.settings import Settings, get_settings
from ..models.schedule import ScheduleGame, ScheduleWeek
from ..models.scoreboard import Scoreboard, ScoreboardGame, Team, Teams
from ..store.schedule_store import ScheduleStore, create_schedule_store
from ..store.state_store import StateStore, create_state_store


class ScoreboardService:
    def __init__(self, settings: Settings, schedule_store: ScheduleStore, state_store: StateStore):
        self.settings = settings
        self.schedule_store = schedule_store
        self.state_store = state_store

    def get_scoreboard(self) -> Scoreboard:
        state = self.state_store.get_state()

        week_key = f"W{state.current_week:02d}"
        schedule_week = self.schedule_store.get_schedule_week(state.current_season, week_key)

        if not schedule_week:
            raise Exception("Unable to find schedule week")

        data = requests.get(self.settings.realtime_schedule_url).json()

        return load_scoreboard(schedule_week, data)


def load_scoreboard(schedule_week: ScheduleWeek, data: dict) -> Scoreboard:
    games = map_games(schedule_week, data)
    focus_game = get_focus_game(games)
    teams = create_teams(games)

    return Scoreboard(
        focus_game=focus_game,
        games=games,
        teams=teams,
    )


def map_games(schedule_week: ScheduleWeek, scoreboard_data: dict) -> list[ScoreboardGame]:
    games = []
    week_data: dict = None

    schedule_games = {x.realtime_source_id: x for x in schedule_week.games}

    for week_data in scoreboard_data:
        if week_data["type"] == "REG" and week_data["number"] == schedule_week.week_number:
            break

    if week_data is None:
        raise Exception(f"Unable to find week {schedule_week.week_number} in scoreboard data")

    for game_data in week_data["tournaments"]:
        schedule_game = schedule_games.get(game_data["id"])
        if schedule_game is None:
            raise Exception(f"Unable to find game {game_data['id']} in schedule")

        games.append(map_game(schedule_game, game_data))

    return games


def map_game(schedule_game: ScheduleGame, game_data: dict) -> ScoreboardGame:
    status = map_status(game_data["status"])
    started = status not in ["scheduled", "postponed"]
    complete = status == "final"

    return ScoreboardGame(
        game_id=schedule_game.game_id,
        game_date=schedule_game.date_start,
        away_abbr=schedule_game.away_abbr,
        home_abbr=schedule_game.home_abbr,
        away_score=game_data["awaySquad"]["score"],
        home_score=game_data["homeSquad"]["score"],
        status=status,
        started=started,
        complete=complete,
        quarter=game_data["activePeriod"],
        clock=game_data["clock"],
    )


def map_status(status: str) -> str:
    active_statuses = ["first_quarter", "second_quarter", "third_quarter", "fourth_quarter", "overtime"]
    if status in active_statuses:
        return "active"
    else:
        return status


def get_focus_game(games: list[ScoreboardGame]) -> Optional[ScoreboardGame]:
    # returns the first scheduled or active game
    focus_statuses = ["scheduled", "first_quarter", "second_quarter", "third_quarter", "fourth_quarter", "overtime"]
    for game in games:
        if game.status in focus_statuses:
            return game

    return None


def create_teams(games: list[ScoreboardGame]) -> Teams:
    team_data = {}

    locked_statuses = ["first_quarter", "second_quarter", "third_quarter", "fourth_quarter", "overtime", "complete"]
    locked_count = 0
    for game in games:
        locked = game.status in locked_statuses
        if locked:
            locked_count += 1
        team_data[game.away_abbr] = Team(opponent=game.home_abbr, locked=locked, game=game, is_at_home=False)
        team_data[game.home_abbr] = Team(opponent=game.away_abbr, locked=locked, game=game, is_at_home=True)

    teams = Teams(**team_data)

    all_locked = locked_count == len(games)
    if all_locked:
        teams.lock_all()

    return teams


def create_scoreboard_service(
    settings: Settings = Depends(get_settings),
    schedule_store: ScheduleStore = Depends(create_schedule_store),
    state_store: StateStore = Depends(create_state_store),
) -> ScoreboardService:
    return ScoreboardService(
        settings=settings,
        schedule_store=schedule_store,
        state_store=state_store,
    )
