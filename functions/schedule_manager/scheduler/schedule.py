

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
        now = datetime.now().replace(tzinfo=pytz.timezone("America/Toronto"))

        if self.preseason.date_start <= now < self.preseason.date_end:
            self.is_preseason = True
            self.current_week = get_current_week(self.preseason, now)

        if self.regular_season.date_start <= now < self.regular_season.date_end:
            self.is_regular_season = True
            self.current_week = get_current_week(self.regular_season, now)

        if self.playoffs.date_start <= now < self.playoffs.date_end:
            self.is_playoffs = True
            self.current_week = get_current_week(self.playoffs, now)

        if now > self.playoffs.date_end or now < self.preseason.date_start:
            self.is_offseason = True


def get_current_week(current_segment: Segment, now: datetime) -> Week:
    for week in current_segment.weeks.values():
        if week.date_start <= now < week.date_end:
            return week
