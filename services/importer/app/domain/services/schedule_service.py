from __future__ import annotations

import requests
from dateutil import parser
from fastapi import Depends
from strivelogger import StriveLogger

from app.config.settings import Settings, get_settings
from app.domain.models.schedule import ByeWeeks, Schedule, ScheduleGame, ScheduleWeek

from ..models.game_id import create_game_id


class ScheduleService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def get_schedule(self) -> Schedule:
        StriveLogger.info("Getting schedule from primary source")
        realtime_source_data = self.get_realtime_source_data()
        boxscore_source_data = self.get_boxscore_source_date()

        return create_schedule(realtime_source_data, boxscore_source_data)

    def get_realtime_source_data(self) -> dict:
        return requests.get(self.settings.realtime_schedule_url).json()

    def get_boxscore_source_date(self) -> dict:
        return requests.get(
            self.settings.boxscore_schedule_url,
            headers={
                "Referer": self.settings.boxscore_source_referer,
            },
        ).json()


def create_schedule(realtime_source_data: dict, boxscore_source_data: dict) -> Schedule:
    weeks: dict[str, ScheduleWeek] = {}

    year = realtime_source_data[0]["startDate"].split("-")[0]
    boxscore_source_season_id: str | None = None

    for seasons in boxscore_source_data["datepicker"]["activeSeasons"]:
        if seasons["seasonName"] == str(year):
            boxscore_source_season_id = seasons["editionId"]

    game_number = 1
    for realtime_source_week in realtime_source_data:
        if realtime_source_week["type"] != "REG":
            continue

        week_number = realtime_source_week["number"]

        key = f"Week {week_number}"
        boxscore_week = boxscore_source_data["datepicker"]["matchSortByWeek"].get(key)

        if not boxscore_week:
            raise ValueError(f"Boxscore week not found for key '{key}'")

        week_key = f"W{str(week_number).zfill(2)}"
        week = ScheduleWeek(week_number=week_number, games=[])
        weeks[week_key] = week

        index = 0
        for realtime_source_game in realtime_source_week["tournaments"]:
            boxscore_source_game = boxscore_week[index]

            week.games.append(map_game(realtime_source_game, boxscore_source_game, week_number, game_number))

            game_number += 1
            index += 1

    return Schedule(
        year=year,
        boxscore_source_season_id=boxscore_source_season_id,
        weeks=weeks,
        bye_weeks=create_bye_weeks(weeks.values()),
    )


def create_bye_weeks(weeks: list[ScheduleWeek]) -> ByeWeeks:
    bye_weeks = ByeWeeks()

    for week in weeks:
        bye_weeks.add_byes(week.week_number, week.bye_teams)

    return bye_weeks


def map_game(realtime_source_data: dict, boxscore_source_data: dict, week_number: int, game_number: int) -> ScheduleGame:
    game_date = parser.isoparse(realtime_source_data["date"])
    year = game_date.year

    game_id = create_game_id(year, week_number, game_number)
    realtime_source_id = realtime_source_data["id"]
    boxscore_source_id = boxscore_source_data["matchId"]

    away_abbr = realtime_source_data["awaySquad"]["shortName"].lower()
    home_abbr = realtime_source_data["homeSquad"]["shortName"].lower()

    # sanity check
    boxscore_source_away = map_boxscore_source_team_id(boxscore_source_data["awayTeamId"])
    boxscore_source_home = map_boxscore_source_team_id(boxscore_source_data["homeTeamId"])

    assert away_abbr == boxscore_source_away, f"Away team mismatch: expected '{away_abbr}', got '{boxscore_source_away}'"
    assert home_abbr == boxscore_source_home, f"Home team mismatch: expected '{home_abbr}', got '{boxscore_source_home}'"

    return ScheduleGame(
        game_id=game_id,
        realtime_source_id=realtime_source_id,
        boxscore_source_id=boxscore_source_id,
        date_start=game_date,
        week=week_number,
        game_number=game_number,
        away_abbr=away_abbr,
        home_abbr=home_abbr,
    )


def map_boxscore_source_team_id(team_id: str) -> str:
    match team_id:
        case "/sport/football/team:241":
            return "bc"

        case "/sport/football/team:243":
            return "cgy"

        case "/sport/football/team:242":
            return "edm"

        case "/sport/football/team:246":
            return "ham"

        case "/sport/football/team:249":
            return "mtl"

        case "/sport/football/team:947":
            return "ott"

        case "/sport/football/team:244":
            return "ssk"

        case "/sport/football/team:247":
            return "tor"

        case "/sport/football/team:245":
            return "wpg"

        case _:
            raise ValueError(f"Unknown team id '{team_id}'")


def create_schedule_service(
    settings: Settings = Depends(get_settings),
) -> ScheduleService:
    return ScheduleService(settings=settings)
