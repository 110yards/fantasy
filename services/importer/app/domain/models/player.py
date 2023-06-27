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


class Position(BaseModel):
    position_id: int
    offence_defence_or_special: str
    abbreviation: str
    description: str

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Position):
            return False

        return self.position_id == __value.position_id

    @staticmethod
    def quarterback():
        return Position(position_id=1, offence_defence_or_special="O", abbreviation="QB", description="Quarterback")

    @staticmethod
    def runningback():
        return Position(position_id=2, offence_defence_or_special="O", abbreviation="RB", description="Running Back")

    @staticmethod
    def fullback():
        return Position(position_id=3, offence_defence_or_special="O", abbreviation="FB", description="Full Back")

    @staticmethod
    def widereceiver():
        return Position(position_id=8, offence_defence_or_special="O", abbreviation="WR", description="Wide Receiver")

    @staticmethod
    def defensiveback():
        return Position(position_id=12, offence_defence_or_special="D", abbreviation="DB", description="Defensive Back")

    def defensiveend():
        return Position(position_id=7, offence_defence_or_special="D", abbreviation="DE", description="Defensive End")

    @staticmethod
    def defensiveline():
        return Position(position_id=13, offence_defence_or_special="D", abbreviation="DL", description="Defensive Lineman")

    @staticmethod
    def kicker():
        return Position(position_id=16, offence_defence_or_special="S", abbreviation="K", description="Kicker")

    @staticmethod
    def offensiveline():
        return Position(position_id=5, offence_defence_or_special="O", abbreviation="OL", description="Offensive Lineman")

    @staticmethod
    def punter():
        return Position(position_id=14, offence_defence_or_special="S", abbreviation="P", description="Punter")

    @staticmethod
    def linebacker():
        return Position(position_id=11, offence_defence_or_special="D", abbreviation="LB", description="Linebacker")

    @staticmethod
    def longsnapper():
        return Position(position_id=17, offence_defence_or_special="S", abbreviation="LS", description="Long Snapper")

    @staticmethod
    def defensivetackle():
        return Position(position_id=18, offence_defence_or_special="D", abbreviation="DT", description="Defensive Tackle")

    @staticmethod
    def tackle():
        return Position(position_id=24, offence_defence_or_special="D", abbreviation="T", description="Tackle")

    @staticmethod
    def tightend():
        return Position(position_id=26, offence_defence_or_special="O", abbreviation="TE", description="Tight End")

    @staticmethod
    def safety():
        return Position(position_id=23, offence_defence_or_special="D", abbreviation="S", description="Safety")

    @staticmethod
    def center():
        return Position(position_id=19, offence_defence_or_special="O", abbreviation="C", description="Center")

    @staticmethod
    def guard():
        return Position(position_id=20, offence_defence_or_special="O", abbreviation="G", description="Guard")

    @staticmethod
    def unknown():
        return Position(position_id=0, offence_defence_or_special="U", abbreviation="U", description="Unknown")


# class Team(BaseModel):
#     abbreviation: str
#     location: Optional[str] = ""
#     nickname: Optional[str] = ""

#     def __eq__(self, other: Any) -> bool:
#         if not isinstance(other, Team):
#             return False

#         return self.abbreviation == other.abbreviation

#     def __hash__(self) -> int:
#         return hash(repr(self))

#     @staticmethod
#     def free_agent():
#         return Team(abbreviation="FA")

#     @staticmethod
#     def bc():
#         return Team(abbreviation="BC", location="BC", nickname="Lions")

#     @staticmethod
#     def cgy():
#         return Team(abbreviation="CGY", location="Calgary", nickname="Stampeders")

#     @staticmethod
#     def edm():
#         return Team(abbreviation="EDM", location="Edmonton", nickname="Elks")

#     @staticmethod
#     def ham():
#         return Team(abbreviation="HAM", location="Hamilton", nickname="Tiger-Cats")

#     @staticmethod
#     def mtl(uniform: Optional[int] = None):
#         return Team(team_id=5, abbreviation="MTL", location="Montreal", nickname="Alouettes", uniform=uniform)

#     @staticmethod
#     def ott():
#         return Team(abbreviation="OTT", location="Ottawa", nickname="Redblacks")

#     @staticmethod
#     def ssk():
#         return Team(abbreviation="SSK", location="Saskatchewan", nickname="Roughriders")

#     @staticmethod
#     def tor():
#         return Team(abbreviation="TOR", location="Toronto", nickname="Argonauts")

#     @staticmethod
#     def wpg():
#         return Team(abbreviation="WPG", location="Winnipeg", nickname="Blue Bombers")


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
    seasons: list[int] = []
    injury_status: Optional[InjuryDetails]
    boxscore_source_id: str

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
        return hashlib.md5(json.dumps(self.json()).encode("utf-8")).hexdigest()
