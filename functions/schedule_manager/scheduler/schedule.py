

from datetime import datetime
import enum
import hashlib
import json
from typing import Dict, List
from pydantic import BaseModel
import pytz


class EventType(BaseModel):
    event_type_id: int
    name: str
    title: str


class Team(BaseModel):
    team_id: int
    location: str
    nickname: str
    abbreviation: str


class Game(BaseModel):
    game_id: int
    date_start: datetime
    game_number: int
    week: int
    season: int
    event_type: EventType
    team_1: Team
    team_2: Team


class WeekType(str, enum.Enum):
    preseason = "preseason"
    regular_season = "regular_season"
    playoffs = "playoffs"
    offseason = "offseason"


class Week(BaseModel):
    week_number: int
    week_type: WeekType
    date_start: datetime = None
    date_end: datetime = None
    games: List[Game] = []


class Segment(BaseModel):
    type: WeekType
    weeks: Dict[int, Week] = {}
    date_start: datetime = None
    date_end: datetime = None


class Schedule(BaseModel):
    season: int
    hash: str = ""
    current_week: Week = None
    is_preseason: bool = False
    is_regular_season: bool = False
    is_playoffs: bool = False
    is_offseason: bool = False
    preseason: Segment = None
    regular_season: Segment = None
    playoffs: Segment = None

    def calculate_hash(self):
        self.hash = hashlib.md5(json.dumps(self.json()).encode("utf-8")).hexdigest()

    def serialize(self) -> dict:
        return json.loads(self.json())

    def set_state(self, sim_segment: WeekType, sim_week: int):
        now = cfl_time(datetime.now())

        if sim_segment:
            print(f"Simulating {sim_segment} week {sim_week}")
            self.is_preseason = sim_segment == WeekType.preseason
            self.is_regular_season = sim_segment == WeekType.regular_season
            self.is_playoffs = sim_segment == WeekType.playoffs
        else:
            self.is_preseason = is_active_segment(now, self.preseason)
            self.is_regular_season = is_active_segment(now, self.regular_season)
            self.is_playoffs = is_active_segment(now, self.playoffs)

        self.is_offseason = is_offseason(self)

        self.current_week = get_current_week(self, now, sim_week)


def cfl_time(from_time: datetime) -> datetime:
    return from_time.replace(tzinfo=pytz.timezone("America/Toronto"))


def is_offseason(schedule: Schedule) -> bool:
    return not schedule.is_preseason and not schedule.is_regular_season and not schedule.is_playoffs


def is_active_segment(now: datetime, segment: Segment) -> bool:
    return segment.date_start <= now < segment.date_end


def get_current_week(schedule: Schedule, now: datetime, sim_week: int) -> Week:

    if schedule.is_preseason:
        return schedule.preseason.weeks[sim_week] if sim_week else get_week_from_segment(schedule.preseason, now)

    if schedule.is_regular_season:
        return schedule.regular_season.weeks[sim_week] if sim_week else get_week_from_segment(schedule.regular_season, now)

    if schedule.is_playoffs:
        return schedule.playoffs.weeks[sim_week] if sim_week else get_week_from_segment(schedule.playoffs, now)

    return Week(week_number=0, week_type=WeekType.offseason)


def get_week_from_segment(current_segment: Segment, now: datetime) -> Week:
    for week in current_segment.weeks.values():
        if week.date_start <= now < week.date_end:
            return week
