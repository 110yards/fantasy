import hashlib
import json
from datetime import datetime

from pydantic import BaseModel, computed_field


class ScheduleGame(BaseModel):
    game_id: str
    realtime_source_id: int
    boxscore_source_id: str
    date_start: datetime
    game_number: int
    week: int
    away_abbr: str
    home_abbr: str


class ScheduleWeek(BaseModel):
    week_number: int
    games: list[ScheduleGame]

    @computed_field
    @property
    def bye_teams(self) -> list[str]:
        teams = ["bc", "cgy", "edm", "ham", "mtl", "ott", "ssk", "tor", "wpg"]
        for game in self.games:
            teams.remove(game.away_abbr)
            teams.remove(game.home_abbr)

        return teams


class ByeWeeks(BaseModel):
    bc: list[int] = []
    cgy: list[int] = []
    edm: list[int] = []
    ham: list[int] = []
    mtl: list[int] = []
    ott: list[int] = []
    ssk: list[int] = []
    tor: list[int] = []
    wpg: list[int] = []

    def add_byes(self, week_number: int, teams: list[str]) -> None:
        for team in teams:
            getattr(self, team).append(week_number)


class Schedule(BaseModel):
    year: int
    boxscore_source_season_id: str
    weeks: dict[str, ScheduleWeek]
    bye_weeks: ByeWeeks

    @computed_field
    @property
    def week_count(self) -> int:
        return len(self.weeks)

    def hash(self) -> str:
        return hashlib.md5(json.dumps(self.json()).encode("utf-8")).hexdigest()

    def get_week(self, week_number: int) -> ScheduleWeek:
        return self.weeks[self.week_key(week_number)]

    @staticmethod
    def week_key(week_number: int) -> str:
        return f"W{str(week_number).zfill(2)}"
