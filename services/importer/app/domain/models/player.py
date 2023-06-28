from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, computed_field

# class School(BaseModel):
#     school_id: Optional[int]
#     name: Optional[str]


class Position(str, Enum):
    quarterback = "qb"
    runningback = "rb"
    fullback = "fb"
    widereceiver = "wr"
    defensiveback = "db"
    defensiveend = "de"
    defensiveline = "dl"
    kicker = "k"
    offensiveline = "ol"
    punter = "p"
    linebacker = "lb"
    longsnapper = "ls"
    defensivetackle = "dt"
    tackle = "t"
    tightend = "te"
    safety = "s"
    center = "c"
    guard = "g"


# class SeasonDefence(BaseModel):
#     season: int
#     team_abbreviation: str
#     games_played: int
#     tackles_total: int
#     tackles_yards: int
#     tackles_defensive: int
#     tackles_specialteams: int
#     tackles_for_loss: int
#     sacks_qb_made: int
#     interceptions_made: int
#     interceptions_yards: int
#     interceptions_long: int
#     interceptions_touchdowns: int
#     interceptions_touchdowns_long: int
#     fumbles_forced: int
#     fumble_returns: int
#     fumble_returns_yards: int
#     fumble_returns_long: int
#     fumble_returns_touchdowns: int
#     fumble_returns_touchdowns_long: int
#     passes_knocked_down: int


# class SeasonFieldGoals(BaseModel):
#     season: int
#     team_abbreviation: str
#     games_played: int
#     field_goals_attempts: int
#     field_goals_made: int
#     field_goals_long: int
#     field_goals_singles: int
#     field_goals_blocked: int
#     field_goals_made_01_19: int
#     field_goals_made_20_29: int
#     field_goals_made_30_39: int
#     field_goals_made_40_49: int
#     field_goals_made_50_plus: int
#     extra_point_attempts: int
#     extra_point_made: int
#     extra_point_yards: int
#     points: int


# class SeasonPunts(BaseModel):
#     season: int
#     team_abbreviation: str
#     games_played: int
#     punts: int
#     punts_yards: int
#     punts_net_yards: int
#     punts_long: int
#     punts_singles: int
#     punts_blocked: int
#     punts_in_10: int
#     punts_in_20: int
#     punts_returned: int


# class SeasonKickoffs(BaseModel):
#     season: int
#     team_abbreviation: str
#     games_played: int
#     kickoffs: int
#     kickoffs_yards: int
#     kickoffs_net_yards: int
#     kickoffs_long: int
#     kickoffs_singles: int
#     kickoffs_onside: int


# class SeasonPassing(BaseModel):
#     season: int
#     team_abbreviation: str
#     games_played: int
#     pass_attempts: int
#     pass_completions: int
#     pass_percentage: str
#     pass_net_yards: int
#     pass_long: int
#     pass_touchdowns: int
#     pass_touchdowns_long: int
#     pass_interceptions: int
#     pass_fumbles: int
#     pass_efficiency: str
#     pass_interceptions_percentage: str


# class SeasonRushing(BaseModel):
#     season: int
#     team_abbreviation: str
#     games_played: int
#     rush_attempts: int
#     rush_yards: int
#     rush_average: str
#     rush_long: int
#     rush_touchdowns: int
#     rush_touchdowns_long: int
#     rush_min_10: int
#     rush_min_20: int


# class SeasonPuntReturns(BaseModel):
#     season: int
#     team_abbreviation: str
#     games_played: int
#     punt_returns: int
#     yards: int
#     average: str
#     long: int
#     touchdowns: int
#     touchdowns_long: int


# class SeasonKickoffReturns(BaseModel):
#     season: int
#     team_abbreviation: str
#     games_played: int
#     kickoff_returns: int
#     yards: int
#     average: str
#     long: int
#     touchdowns: int
#     touchdowns_long: int


# class SeasonMissedFgReturn(BaseModel):
#     season: int
#     team_abbreviation: str
#     games_played: int
#     missed_fg_returns: int
#     yards: int
#     average: str
#     long: int
#     touchdowns: int
#     touchdowns_long: int


# class SeasonReceiving(BaseModel):
#     season: int
#     team_abbreviation: str
#     games_played: int
#     receive_attempts: int
#     receive_caught: int
#     receive_average: str
#     receive_yards: int
#     receive_long: int
#     receive_touchdowns: int
#     receive_touchdowns_long: int
#     receive_second_down_conversions: int
#     receive_fumbles: int
#     receive_yards_after_catch: int
#     receive_min_30: int


# class Seasons(BaseModel):
#     defence: Optional[List[SeasonDefence]]
#     field_goals: Optional[List[SeasonFieldGoals]]
#     punts: Optional[List[SeasonPunts]]
#     kickoffs: Optional[List[SeasonKickoffs]]
#     passing: Optional[List[SeasonPassing]]
#     rushing: Optional[List[SeasonRushing]]
#     punt_returns: Optional[List[SeasonPuntReturns]]
#     kickoff_returns: Optional[List[SeasonKickoffReturns]]
#     missed_fg_returns: Optional[List[SeasonMissedFgReturn]]
#     receiving: Optional[List[SeasonReceiving]]


# class GameDefence(BaseModel):
#     game_id: int
#     game_date: str
#     week: int
#     season: int
#     opponent_team_abbreviation: str
#     tackles_total: int
#     tackles_yards: int
#     tackles_defensive: int
#     tackles_specialteams: int
#     tackles_for_loss: int
#     sacks_qb_made: int
#     interceptions_made: int
#     interceptions_yards: int
#     interceptions_long: int
#     interceptions_touchdowns: int
#     interceptions_touchdowns_long: int
#     fumbles_forced: int
#     fumble_returns: int
#     fumble_returns_yards: int
#     fumble_returns_long: int
#     fumble_returns_touchdowns: int
#     fumble_returns_touchdowns_long: int
#     passes_knocked_down: int


# class GameFieldGoals(BaseModel):
#     game_id: int
#     game_date: str
#     week: int
#     season: int
#     opponent_team_abbreviation: str
#     field_goals_attempts: int
#     field_goals_made: int
#     field_goals_long: int
#     field_goals_singles: int
#     field_goals_blocked: int
#     field_goals_made_01_19: int
#     field_goals_made_20_29: int
#     field_goals_made_30_39: int
#     field_goals_made_40_49: int
#     field_goals_made_50_plus: int
#     extra_point_attempts: int
#     extra_point_made: int
#     extra_point_yards: int
#     points: int


# class GamePunts(BaseModel):
#     game_id: int
#     game_date: str
#     week: int
#     season: int
#     opponent_team_abbreviation: str
#     punts: int
#     punts_yards: int
#     punts_net_yards: int
#     punts_long: int
#     punts_singles: int
#     punts_blocked: int
#     punts_in_10: int
#     punts_in_20: int
#     punts_returned: int


# class GameKickoffs(BaseModel):
#     game_id: int
#     game_date: str
#     week: int
#     season: int
#     opponent_team_abbreviation: str
#     kickoffs: int
#     kickoffs_yards: int
#     kickoffs_net_yards: int
#     kickoffs_long: int
#     kickoffs_singles: int
#     kickoffs_onside: int


# class GamePassing(BaseModel):
#     game_id: int
#     game_date: str
#     week: int
#     season: int
#     opponent_team_abbreviation: str
#     pass_attempts: int
#     pass_completions: int
#     pass_percentage: str
#     pass_net_yards: int
#     pass_long: int
#     pass_touchdowns: int
#     pass_touchdowns_long: int
#     pass_interceptions: int
#     pass_fumbles: int
#     pass_efficiency: str
#     pass_interceptions_percentage: str


# class GameRushing(BaseModel):
#     game_id: int
#     game_date: str
#     week: int
#     season: int
#     opponent_team_abbreviation: str
#     rush_attempts: int
#     rush_yards: int
#     rush_average: str
#     rush_long: int
#     rush_touchdowns: int
#     rush_touchdowns_long: int
#     rush_min_10: int
#     rush_min_20: int


# class GamePuntReturns(BaseModel):
#     game_id: int
#     game_date: str
#     week: int
#     season: int
#     opponent_team_abbreviation: str
#     punt_returns: int
#     yards: int
#     average: str
#     long: int
#     touchdowns: int
#     touchdowns_long: int


# class GameKickoffReturns(BaseModel):
#     game_id: int
#     game_date: str
#     week: int
#     season: int
#     opponent_team_abbreviation: str
#     kickoff_returns: int
#     yards: int
#     average: str
#     long: int
#     touchdowns: int
#     touchdowns_long: int


# class GameMissFgReturns(BaseModel):
#     game_id: int
#     game_date: str
#     week: int
#     season: int
#     opponent_team_abbreviation: str
#     missed_fg_returns: int
#     yards: int
#     average: str
#     long: int
#     touchdowns: int
#     touchdowns_long: int


# class GameReceiving(BaseModel):
#     game_id: int
#     game_date: str
#     week: int
#     season: int
#     opponent_team_abbreviation: str
#     receive_attempts: int
#     receive_caught: int
#     receive_average: str
#     receive_yards: int
#     receive_long: int
#     receive_touchdowns: int
#     receive_touchdowns_long: int
#     receive_second_down_conversions: int
#     receive_fumbles: int
#     receive_yards_after_catch: int
#     receive_min_30: int


# class GameByGame(BaseModel):
#     defence: Optional[List[GameDefence]]
#     field_goals: Optional[List[GameFieldGoals]]
#     punts: Optional[List[GamePunts]]
#     kickoffs: Optional[List[GameKickoffs]]
#     passing: Optional[List[GamePassing]]
#     rushing: Optional[List[GameRushing]]
#     punt_returns: Optional[List[GamePuntReturns]]
#     kickoff_returns: Optional[List[GameKickoffReturns]]
#     missed_fg_returns: Optional[List[GameMissFgReturns]]
#     receiving: Optional[List[GameReceiving]]


class InjuryStatus(str, Enum):
    Probable = "probable"
    Questionable = "questionable"
    Out = "out"
    InjuredSixGames = "six-game"


class InjuryDetails(BaseModel):
    status_id: InjuryStatus
    text: str
    last_updated: str
    injury: str


class Player(BaseModel):
    first_name: str
    last_name: str
    birth_date: Optional[datetime]
    birth_place: Optional[str]
    height: Optional[str] = None
    weight: Optional[int] = None
    canadian_player: bool
    position: Position
    team_abbr: Optional[str]
    alternate_computed_ids: list[str] = []
    uniform: Optional[int] = None
    school: Optional[str]
    seasons: list[int]
    injury_status: Optional[InjuryDetails]
    boxscore_source_id: str
    last_updated: Optional[datetime] = None

    @computed_field
    @property
    def computed_id_clear(self) -> str:
        return f"{self.name_slug}-{self.birth_date_unix}"

    @computed_field
    @property
    def player_id(self) -> str:
        id_clear = self.computed_id_clear
        return hashlib.md5(id_clear.encode("utf-8")).hexdigest()

    @computed_field
    @property
    def name_slug(self) -> str:
        slug = f"{self.first_name}-{self.last_name}"
        # Remove any non-alphanumeric characters
        slug = re.sub(r"[^a-zA-Z0-9]+", "", slug)
        return slug.lower()

    @computed_field
    @property
    def birth_date_unix(self) -> int:
        return int(self.birth_date.timestamp())

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @computed_field
    @property
    def is_free_agent(self) -> bool:
        return not self.team_abbr

    def hash(self) -> str:
        to_compare = self.model_dump_json(
            exclude={"last_updated"},
        )

        return hashlib.md5(json.dumps(to_compare).encode("utf-8")).hexdigest()
