from __future__ import annotations

import requests
from dateutil import parser
from fastapi import Depends
from strivelogger import StriveLogger

from app.config.settings import Settings, get_settings
from app.core import game_mappings
from app.domain.models.game import EventStatus, EventType, Game, Team
from app.domain.models.schedule import Schedule


class ScheduleService:
    def __init__(self, use_tsn_schedule: bool):
        self.use_tsn_schedule = use_tsn_schedule

    def get_schedule(self) -> Schedule:
        return get_from_tsn() if self.use_tsn_schedule else get_from_cfl()


#########################################
# TSN - not updating live currently
def get_from_tsn() -> Schedule:
    StriveLogger.info("Getting schedule from TSN")
    page = 4

    games: list[Game] = []
    year = 0

    while True:
        url = f"https://stats.sports.bellmedia.ca/sports/football/leagues/cfl/schedule/subset/dates?brand=tsn&type=json&dateOrId={page}&toAdd=99"
        response = requests.get(url)

        if response.headers.get("Content-Type") != "application/json":
            break

        data: dict = response.json()
        if len(data) == 0:
            break

        games.extend(map_tsn_week(data))

        if year == 0:
            year = data[str(page)]["season"]

        page += len(data)

    return Schedule(
        year=year,
        games=games,
    )


def map_tsn_week(data: dict) -> list[Game]:
    games = []

    for key in data.keys():
        week = data[key]
        for game in week["events"]:
            games.append(map_tsn_game(week, game))

    return games


def map_tsn_game(week_data: dict, game_data: dict) -> Game:
    # game_id = game_data["id"] if year > 2023 else mappings_2023[str(game_data["id"])]

    return Game(
        tsn_game_id=game_data["eventId"],
        date_start=game_data["dateGMT"] + "+00:00",
        week=week_data["eventGrouping"],
        season=week_data["season"],
        event_type=map_tsn_game_type(week_data["seasonType"]),
        event_status=map_tsn_event_status(game_data["status"], "0:00"),
        team_1=map_tsn_team(game_data["awayEventResult"], is_at_home=False),
        team_2=map_tsn_team(game_data["homeEventResult"], is_at_home=True),
    )


def map_tsn_game_type(type: str) -> EventType:
    if type == "Exhibition":
        return EventType(
            event_type_id=0,
            name="Preseason",
        )

    if type == "Regular Season":
        return EventType(
            event_type_id=1,
            name="Regular Season",
        )

    raise NotImplementedError(f"Event type {type} not implemented")


def map_tsn_event_status(status: str, clock: str) -> EventStatus:
    if status == "Pre-Game":
        return EventStatus(
            event_status_id=0,
            name="Pre-Game",
            is_active=False,
        )

    if status == "Final":
        return EventStatus(
            event_status_id=1,
            name="Final",
            is_active=False,
        )

    # if status in ["first_quarter", "second_quarter", "third_quarter", "fourth_quarter", "overtime"]:
    #     if status == "first_quarter":
    #         quarter = 1
    #     elif status == "second_quarter":
    #         quarter = 2
    #     elif status == "third_quarter":
    #         quarter = 3
    #     elif status == "fourth_quarter":
    #         quarter = 4
    #     elif status == "overtime":
    #         quarter = 5
    #     else:
    #         quarter = None

    #     clock_parts = clock.split(":")
    #     minutes = int(clock_parts[0])
    #     seconds = int(clock_parts[1])

    #     return EventStatus(
    #         event_status_id=2,
    #         name="In Progress",
    #         is_active=True,
    #         quarter=quarter,
    #         minutes=minutes,
    #         seconds=seconds,
    #     )

    raise NotImplementedError(f"Event status {status} not implemented")


def map_tsn_team(team_data: dict, is_at_home: bool) -> Team:
    score = team_data["score"] or 0
    match team_data["competitor"]["competitorId"]:
        case 1069:
            return Team.cgy(score, is_at_home)
        case 1070:
            return Team.edm(score, is_at_home)
        case 38354:
            return Team.ott(score, is_at_home)
        case 1072:
            return Team.mtl(score, is_at_home)
        case 1071:
            return Team.ham(score, is_at_home)
        case 1074:
            return Team.tor(score, is_at_home)
        case 1075:
            return Team.wpg(score, is_at_home)
        case 1073:
            return Team.ssk(score, is_at_home)
        case 1068:
            return Team.bc(score, is_at_home)
        case _:
            raise NotImplementedError(f"Team {team_data['id']} not implemented")


#########################################
# CFL / Genius


def get_from_cfl() -> Schedule:
    StriveLogger.info("Getting schedule from CFL")
    data = requests.get("https://cflscoreboard.cfl.ca/json/scoreboard/rounds.json").json()

    return map_genius_scoreboard(data)


def map_genius_scoreboard(data: dict) -> Schedule:
    games: list[Game] = []
    game_number = 1
    for week in data:
        if week["type"] != "REG":
            continue

        for game in week["tournaments"]:
            games.append(map_genius_game(week, game, game_number))
            game_number += 1

    year = data[0]["startDate"].split("-")[0]
    games = {game.game_id: game for game in games}

    return Schedule(
        year=year,
        games=games,
    )


def map_genius_game(week_data: dict, game_data: dict, game_number: int) -> Game:
    game_date = parser.isoparse(game_data["date"])
    year = game_date.year
    week = week_data["number"]

    game_id = Game.get_game_id(year, week, game_number)
    cfl_game_id = None if year > 2023 else game_mappings.genius_to_legacy_mappings_2023[str(game_data["id"])]
    tsn_game_id = game_mappings.genius_to_tsn_mappings_2023[str(game_data["id"])]
    genius_game_id = game_data["id"]

    return Game(
        game_id=game_id,
        cfl_game_id=cfl_game_id,
        genius_game_id=genius_game_id,
        tsn_game_id=tsn_game_id,
        date_start=game_data["date"],
        week=week,
        season=year,
        event_type=map_genius_game_type(week_data["type"]),
        event_status=map_genius_event_status(game_data["status"], game_data["clock"]),
        team_1=map_genius_team(game_data["awaySquad"], is_at_home=False),
        team_2=map_genius_team(game_data["homeSquad"], is_at_home=True),
    )


def map_genius_game_type(type: str) -> EventType:
    if type == "PRE":
        return EventType(
            event_type_id=0,
            name="Preseason",
        )

    if type == "REG":
        return EventType(
            event_type_id=1,
            name="Regular Season",
        )

    raise NotImplementedError(f"Event type {type} not implemented")


def map_genius_event_status(status: str, clock: str) -> EventStatus:
    if status == "scheduled":
        return EventStatus(
            event_status_id=1,
            name="Pre-Game",
            is_active=False,
        )

    if status == "complete":
        return EventStatus(
            event_status_id=4,
            name="Final",
            is_active=False,
        )

    if status in ["first_quarter", "second_quarter", "third_quarter", "fourth_quarter", "overtime"]:
        if status == "first_quarter":
            quarter = 1
        elif status == "second_quarter":
            quarter = 2
        elif status == "third_quarter":
            quarter = 3
        elif status == "fourth_quarter":
            quarter = 4
        elif status == "overtime":
            quarter = 5
        else:
            quarter = None

        clock_parts = clock.split(":")
        minutes = int(clock_parts[0])
        seconds = int(clock_parts[1])

        return EventStatus(
            event_status_id=2,
            name="In Progress",
            is_active=True,
            quarter=quarter,
            minutes=minutes,
            seconds=seconds,
        )


def map_genius_team(team_data: dict, is_at_home: bool) -> Team:
    match team_data["id"]:
        case 112939:
            return Team.cgy(team_data["score"], is_at_home)
        case 114347:
            return Team.edm(team_data["score"], is_at_home)
        case 88019:
            return Team.ott(team_data["score"], is_at_home)
        case 86680:
            return Team.mtl(team_data["score"], is_at_home)
        case 83579:
            return Team.ham(team_data["score"], is_at_home)
        case 122345:
            return Team.tor(team_data["score"], is_at_home)
        case 110380:
            return Team.wpg(team_data["score"], is_at_home)
        case 106752:
            return Team.ssk(team_data["score"], is_at_home)
        case 93775:
            return Team.bc(team_data["score"], is_at_home)
        case _:
            raise NotImplementedError(f"Team {team_data['id']} not implemented")


def create_schedule_service(
    settings: Settings = Depends(get_settings),
) -> ScheduleService:
    return ScheduleService(
        use_tsn_schedule=settings.use_tsn_schedule,
    )
