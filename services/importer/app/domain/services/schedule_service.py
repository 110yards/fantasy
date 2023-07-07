from __future__ import annotations

from datetime import datetime

import requests
from dateutil import parser
from fastapi import Depends
from strivelogger import StriveLogger

from app.config.settings import Settings, get_settings
from app.domain.models.schedule import ByeWeeks, Schedule, ScheduleGame, ScheduleWeek

from ..models.game_id import create_game_id
from ..store.state_store import StateStore, create_state_store


class ScheduleService:
    def __init__(self, settings: Settings, state_store: StateStore):
        self.settings = settings
        self.state_store = state_store

    def get_schedule(self) -> Schedule:
        state = self.state_store.get_state()
        year = state.current_season

        is_prior_year = year < datetime.now().year

        if is_prior_year:
            StriveLogger.info("Getting schedule from prior year")
            realtime_source_data = None
            boxscore_source_data = self.get_boxscore_source_data(year)
        else:
            StriveLogger.info("Getting schedule for current year")
            realtime_source_data = self.get_realtime_source_data()
            boxscore_source_data = self.get_boxscore_source_data(year)

        return create_current_schedule(realtime_source_data, boxscore_source_data, year, is_prior_year)

    def get_realtime_source_data(self) -> dict:
        StriveLogger.info(f"Getting realtime source data from url '{self.settings.realtime_schedule_url}'")
        return requests.get(self.settings.realtime_schedule_url).json()

    def get_boxscore_source_data(self, year: int) -> dict:
        url = self.settings.boxscore_schedule_url

        StriveLogger.info(f"Getting boxscore source data from url '{url}'")
        schedule_data = requests.get(url, headers={"Referer": self.settings.boxscore_schedule_url_referer}).json()

        # first request always returns the current year
        # find the editionId
        for season_data in schedule_data["datepicker"]["activeSeasons"]:
            if season_data["seasonName"] == str(year):
                season_id = season_data["editionId"]
                break

        if not season_id:
            raise ValueError(f"Season id not found for year '{year}'")

        url = f"{self.settings.boxscore_schedule_url}&editionId={season_id}"
        schedule_data = requests.get(url, headers={"Referer": self.settings.boxscore_schedule_url_referer}).json()

        url = self.settings.boxscore_teams_url_format.format(season_id=season_id)
        teams_data = requests.get(url, headers={"Referer": self.settings.boxscore_schedule_url_referer}).json()
        schedule_data["teams"] = {x["teamId"]: x for x in teams_data["teams"]["teams"]}

        return schedule_data


def create_current_schedule(realtime_source_data: dict, boxscore_source_data: dict, year: int, prior_year: bool) -> Schedule:
    weeks: dict[str, ScheduleWeek] = {}

    boxscore_source_season_id: str | None = None

    for seasons in boxscore_source_data["datepicker"]["activeSeasons"]:
        if seasons["seasonName"] == str(year):
            boxscore_source_season_id = seasons["editionId"]

    game_number = 1

    realtime_weeks = {week["number"]: week for week in realtime_source_data if week["type"] == "REG"} if realtime_source_data else None

    week_number = 1
    for boxscore_week_key, boxscore_week in boxscore_source_data["datepicker"]["matchSortByWeek"].items():
        if "Pre-Season" in boxscore_week_key:
            continue

        week_key = Schedule.week_key(week_number)

        week = ScheduleWeek(week_number=week_number, games=[])
        weeks[week_key] = week

        realtime_week = realtime_weeks[week_number] if realtime_weeks else None

        index = 0
        for boxscore_source_game in boxscore_week:
            realtime_source_game = realtime_week["tournaments"][index] if realtime_week else None

            week.games.append(map_game(realtime_source_game, boxscore_source_game, week_number, game_number, boxscore_source_data["teams"]))

            game_number += 1
            index += 1

        week_number += 1

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


def map_game(realtime_source_data: dict, boxscore_source_data: dict, week_number: int, game_number: int, boxscore_team_data: dict) -> ScheduleGame:
    game_date = parser.isoparse(boxscore_source_data["dateStart"])
    year = game_date.year

    game_id = create_game_id(year, week_number, game_number)
    realtime_source_id = realtime_source_data["id"] if realtime_source_data else None
    boxscore_source_id = boxscore_source_data["matchId"]

    away_abbr = map_boxscore_source_team_id(boxscore_source_data["awayTeamId"], boxscore_team_data)
    home_abbr = map_boxscore_source_team_id(boxscore_source_data["homeTeamId"], boxscore_team_data)

    # sanity check
    if realtime_source_data:
        realtime_away = realtime_source_data["awaySquad"]["shortName"].lower()
        realtime_home = realtime_source_data["homeSquad"]["shortName"].lower()

        assert away_abbr == realtime_away, f"Away team mismatch: expected '{away_abbr}', got '{realtime_away}'"
        assert home_abbr == realtime_home, f"Home team mismatch: expected '{home_abbr}', got '{realtime_home}'"

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


def map_boxscore_source_team_id(team_id: str, team_data: dict) -> str:
    return team_data[team_id]["teamShortName"].lower()


def create_schedule_service(
    settings: Settings = Depends(get_settings),
    state_store: StateStore = Depends(create_state_store),
) -> ScheduleService:
    return ScheduleService(settings=settings, state_store=state_store)
