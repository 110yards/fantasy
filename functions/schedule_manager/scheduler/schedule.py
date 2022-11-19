

from datetime import datetime
import hashlib
import json
from typing import Dict, List, Literal, Optional
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


class Week(BaseModel):
    week_number: int
    date_start: datetime
    date_end: datetime
    games: List[Game] = []


class Segment(BaseModel):
    type: Literal["preseason", "regular_season", "playoffs"]
    weeks: Dict[int, Week] = {}
    date_start: datetime = None
    date_end: datetime = None


class Schedule(BaseModel):
    season: int
    hash: str = ""
    current_week: Optional[Week] = None
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

    def set_state(self):
        now = cfl_time(datetime.now())

        self.is_preseason = is_active_segment(now, self.preseason)
        self.is_regular_season = is_active_segment(now, self.regular_season)
        self.is_playoffs = is_active_segment(now, self.playoffs.date_start)
        self.is_offseason = is_offseason(self)

        if not self.is_offseason:
            self.current_week = get_current_week(self.playoffs, now)


def cfl_time(from_time: datetime) -> datetime:
    return from_time.replace(tzinfo=pytz.timezone("America/Toronto"))


def is_offseason(schedule: Schedule) -> bool:
    return not schedule.is_preseason and not schedule.is_regular_season and not schedule.is_playoffs


def is_active_segment(now: datetime, segment: Segment) -> bool:
    return segment.date_start <= now < segment.date_end


def get_current_week(schedule: Schedule, now: datetime) -> Week:
    if schedule.is_preseason:
        return get_week_from_segment(schedule.preseason, now)

    if schedule.is_regular_season:
        return get_week_from_segment(schedule.regular_season, now)

    if schedule.is_playoffs:
        return get_week_from_segment(schedule.playoffs, now)


def get_week_from_segment(current_segment: Segment, now: datetime) -> Week:
    for week in current_segment.weeks.values():
        if week.date_start <= now < week.date_end:
            return week
