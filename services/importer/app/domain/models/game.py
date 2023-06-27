from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class EventType(BaseModel):
    event_type_id: int
    name: str
    title: str = ""


class EventStatus(BaseModel):
    event_status_id: int
    name: str
    is_active: bool
    quarter: Optional[int]
    minutes: Optional[int]
    seconds: Optional[int]
    down: Optional[int]
    yards_to_go: Optional[int]

    """
    EVENT_STATUS_PRE_GAME = 1
    EVENT_STATUS_IN_PROGRESS = 2
    EVENT_STATUS_FINAL = 4
    EVENT_STATUS_POSTPONED = 6
    EVENT_STATUS_CANCELLED = 9
    """

    @staticmethod
    def pre_game() -> EventStatus:
        return EventStatus(event_status_id=1, name="Pre-Game", is_active=False)

    @staticmethod
    def in_progress() -> EventStatus:
        return EventStatus(event_status_id=2, name="In Progress", is_active=True)

    @staticmethod
    def final() -> EventStatus:
        return EventStatus(event_status_id=4, name="Final", is_active=False)

    @staticmethod
    def postponed() -> EventStatus:
        return EventStatus(event_status_id=6, name="Postponed", is_active=False)

    @staticmethod
    def cancelled() -> EventStatus:
        return EventStatus(event_status_id=9, name="Cancelled", is_active=False)


class Venue(BaseModel):
    venue_id: int
    name: str


class Weather(BaseModel):
    temperature: int
    sky: str
    wind_speed: str
    wind_direction: str
    field_conditions: str


class CoinToss(BaseModel):
    coin_toss_winner: str
    coin_toss_winner_election: str


class Linescore(BaseModel):
    quarter: int | str
    score: int


class Team(BaseModel):
    team_id: int
    location: str
    nickname: str
    abbreviation: str
    score: int
    linescores: Optional[List[Linescore]]
    is_at_home: bool
    is_winner: Optional[bool]

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Team):
            return False

        return self.team_id == other.team_id

    def __hash__(self) -> int:
        return hash(repr(self))

    @staticmethod
    def bc(score: int, is_at_home: bool):
        return Team(team_id=1, abbreviation="BC", location="BC", nickname="Lions", score=score, is_at_home=is_at_home)

    @staticmethod
    def cgy(score: int, is_at_home: bool):
        return Team(team_id=2, abbreviation="CGY", location="Calgary", nickname="Stampeders", score=score, is_at_home=is_at_home)

    @staticmethod
    def edm(score: int, is_at_home: bool):
        return Team(team_id=3, abbreviation="EDM", location="Edmonton", nickname="Elks", score=score, is_at_home=is_at_home)

    @staticmethod
    def ham(score: int, is_at_home: bool):
        return Team(
            team_id=4,
            abbreviation="HAM",
            location="Hamilton",
            nickname="Tiger-Cats",
            score=score,
            is_at_home=is_at_home,
        )

    @staticmethod
    def mtl(score: int, is_at_home: bool):
        return Team(team_id=5, abbreviation="MTL", location="Montreal", nickname="Alouettes", score=score, is_at_home=is_at_home)

    @staticmethod
    def ott(score: int, is_at_home: bool):
        return Team(team_id=6, abbreviation="OTT", location="Ottawa", nickname="Redblacks", score=score, is_at_home=is_at_home)

    @staticmethod
    def ssk(score: int, is_at_home: bool):
        return Team(
            team_id=7,
            abbreviation="SSK",
            location="Saskatchewan",
            nickname="Roughriders",
            score=score,
            is_at_home=is_at_home,
        )

    @staticmethod
    def tor(score: int, is_at_home: bool):
        return Team(team_id=8, abbreviation="TOR", location="Toronto", nickname="Argonauts", score=score, is_at_home=is_at_home)

    @staticmethod
    def wpg(score: int, is_at_home: bool):
        return Team(
            team_id=9,
            abbreviation="WPG",
            location="Winnipeg",
            nickname="Blue Bombers",
            score=score,
            is_at_home=is_at_home,
        )


class Down(BaseModel):
    down: int
    attempts: int
    yards: int


class TeamOffence(BaseModel):
    offence_possession_time: Optional[str]
    downs: List[Down]


class TeamTurnovers(BaseModel):
    fumbles: int
    interceptions: int
    downs: int


class TeamPassing(BaseModel):
    pass_attempts: int
    pass_completions: int
    pass_net_yards: int
    pass_long: int
    pass_touchdowns: int
    pass_completion_percentage: str
    pass_efficiency: str
    pass_interceptions: int
    pass_fumbles: int


class TeamRushing(BaseModel):
    rush_attempts: int
    rush_net_yards: int
    rush_long: int
    rush_touchdowns: int
    rush_long_touchdowns: int


class TeamReceiving(BaseModel):
    receive_attempts: int
    receive_caught: int
    receive_yards: int
    receive_long: int
    receive_touchdowns: int
    receive_long_touchdowns: int
    receive_yards_after_catch: int
    receive_fumbles: int


class TeamPunts(BaseModel):
    punts: int
    punt_yards: int
    punt_net_yards: int
    punt_long: int
    punt_singles: int
    punts_blocked: int
    punts_in_10: int
    punts_in_20: int
    punts_returned: int


class TeamPuntReturns(BaseModel):
    punt_returns: int
    punt_returns_yards: int
    punt_returns_touchdowns: int
    punt_returns_long: int
    punt_returns_touchdowns_long: int


class TeamKickReturns(BaseModel):
    kick_returns: int
    kick_returns_yards: int
    kick_returns_touchdowns: int
    kick_returns_long: int
    kick_returns_touchdowns_long: int


class TeamFieldGoals(BaseModel):
    field_goal_attempts: int
    field_goal_made: int
    field_goal_yards: int
    field_goal_singles: int
    field_goal_long: int
    field_goal_points: int


class TeamKicking(BaseModel):
    kicks: int
    kick_yards: int
    kicks_net_yards: int
    kicks_long: int
    kicks_singles: int
    kicks_out_of_end_zone: int
    kicks_onside: int


class OnePointConverts(BaseModel):
    attempts: int
    made: int


class TwoPointConverts(BaseModel):
    attempts: int
    made: int


class TeamConverts(BaseModel):
    one_point_converts: OnePointConverts
    two_point_converts: TwoPointConverts


class TeamDefence(BaseModel):
    tackles_total: int
    tackles_defensive: int
    tackles_special_teams: int
    sacks_qb_made: int
    interceptions: int
    fumbles_forced: int
    fumbles_recovered: int
    passes_knocked_down: int
    defensive_touchdowns: int
    defensive_safeties: int


class TeamPenalties(BaseModel):
    total: int
    yards: int
    offence_total: int
    offence_yards: int
    defence_total: int
    defence_yards: int
    special_teams_coverage_total: int
    special_teams_coverage_yards: int
    special_teams_return_total: int
    special_teams_return_yards: int


class GamePlayer(BaseModel):
    first_name: str
    last_name: str
    player_id: Optional[str] = None
    birth_date: Optional[str] = None


class PlayerPassing(BaseModel):
    player: GamePlayer
    pass_attempts: int
    pass_completions: int
    pass_net_yards: int
    pass_touchdowns: int
    pass_interceptions: int
    pass_completion_percentage: str = ""
    pass_efficiency: str = ""
    pass_fumbles: int = 0
    pass_long: int = 0


class PlayerRushing(BaseModel):
    player: GamePlayer
    rush_attempts: int
    rush_net_yards: int
    rush_touchdowns: int
    rush_long: int = 0
    rush_long_touchdowns: int = 0


class PlayerReceiving(BaseModel):
    player: GamePlayer
    receive_caught: int
    receive_yards: int
    receive_long: int
    receive_touchdowns: int
    receive_attempts: int = 0
    receive_long_touchdowns: int = 0
    receive_yards_after_catch: int = 0
    receive_fumbles: int = 0


class PlayerPunts(BaseModel):
    player: GamePlayer
    punts: int
    punt_yards: int
    punt_long: int
    punt_net_yards: int = 0
    punt_singles: int = 0
    punts_blocked: int = 0
    punts_in_10: int = 0
    punts_in_20: int = 0
    punts_returned: int = 0


class PlayerPuntReturns(BaseModel):
    player: GamePlayer
    punt_returns: int
    punt_returns_yards: int
    punt_returns_touchdowns: int
    punt_returns_long: int
    punt_returns_touchdowns_long: int = 0


class PlayerKickReturns(BaseModel):
    player: GamePlayer
    kick_returns: int
    kick_returns_yards: int
    kick_returns_touchdowns: int
    kick_returns_long: int
    kick_returns_touchdowns_long: int = 0


class PlayerFieldGoals(BaseModel):
    player: GamePlayer
    field_goal_attempts: int
    field_goal_made: int
    field_goal_yards: int = 0
    field_goal_singles: int = 0
    field_goal_long: int = 0
    field_goal_missed_list: str = 0
    field_goal_points: int = 0


class PlayerFieldGoalReturns(BaseModel):
    player: GamePlayer
    field_goal_returns: int
    field_goal_returns_yards: int
    field_goal_returns_touchdowns: int
    field_goal_returns_long: int
    field_goal_returns_touchdowns_long: int


class PlayerKicking(BaseModel):
    player: GamePlayer
    kicks: int
    kicks_singles: int
    kick_yards: int = 0
    kicks_net_yards: int = 0
    kicks_long: int = 0
    kicks_out_of_end_zone: int
    kicks_onside: int


class PlayerOnePointConverts(BaseModel):
    player: GamePlayer
    one_point_converts_attempts: int
    one_point_converts_made: int


class PlayerTwoPointConverts(BaseModel):
    player: GamePlayer
    two_point_converts_made: int


class PlayerDefence(BaseModel):
    player: GamePlayer
    tackles_total: int = 0
    tackles_defensive: int
    tackles_special_teams: int = 0
    sacks_qb_made: int
    interceptions: int
    fumbles_forced: int
    fumbles_recovered: int = 0
    passes_knocked_down: int


class GamePlayers(BaseModel):
    passing: Optional[List[PlayerPassing]]
    rushing: Optional[List[PlayerRushing]]
    receiving: Optional[List[PlayerReceiving]]
    punts: Optional[List[PlayerPunts]]
    punt_returns: Optional[List[PlayerPuntReturns]]
    kick_returns: Optional[List[PlayerKickReturns]]
    field_goals: Optional[List[PlayerFieldGoals]]
    field_goal_returns: Optional[List[PlayerFieldGoalReturns]]
    kicking: Optional[List[PlayerKicking]]
    one_point_converts: Optional[List[PlayerOnePointConverts]]
    two_point_converts: Optional[List[PlayerTwoPointConverts]]
    defence: Optional[List[PlayerDefence]]


class BoxscoreTeam(BaseModel):
    abbreviation: str
    team_id: int
    offence: Optional[TeamOffence]
    turnovers: Optional[TeamTurnovers]
    passing: Optional[TeamPassing]
    rushing: Optional[TeamRushing]
    receiving: Optional[TeamReceiving]
    punts: Optional[TeamPunts]
    punt_returns: Optional[TeamPuntReturns]
    kick_returns: Optional[TeamKickReturns]
    field_goals: Optional[TeamFieldGoals]
    kicking: Optional[TeamKicking]
    converts: Optional[TeamConverts]
    defence: Optional[TeamDefence]
    penalties: Optional[TeamPenalties]
    players: GamePlayers


class BoxscoreTeams(BaseModel):
    team_1: BoxscoreTeam
    team_2: BoxscoreTeam


class Boxscore(BaseModel):
    teams: BoxscoreTeams


class Quarterback(BaseModel):
    cfl_central_id: int
    first_name: str
    middle_name: str
    last_name: str
    birth_date: str


class BallCarrier(BaseModel):
    cfl_central_id: int
    first_name: str
    middle_name: str
    last_name: str
    birth_date: str


class PrimaryDefender(BaseModel):
    cfl_central_id: int
    first_name: str
    middle_name: str
    last_name: str
    birth_date: str


class PlayersInPlay(BaseModel):
    quarterback: GamePlayer
    ball_carrier: GamePlayer
    primary_defender: GamePlayer


class Play(BaseModel):
    play_id: int
    play_sequence: int
    quarter: int
    play_clock_start: str
    play_clock_start_in_secs: int
    field_position_start: str
    field_position_end: str
    down: int
    yards_to_go: int
    is_in_red_zone: bool
    team_home_score: int
    team_visitor_score: int
    play_type_id: int
    play_type_description: str
    play_result_type_id: int
    play_result_type_description: str
    play_result_yards: int
    play_result_points: int
    play_success_id: int
    play_success_description: str
    play_change_of_possession_occurred: bool
    team_abbreviation: str
    team_id: int
    players: PlayersInPlay
    play_summary: str


class RosterPlayer(BaseModel):
    player_id: str
    cfl_central_id: Optional[int]
    first_name: str
    middle_name: str = ""
    last_name: str
    birth_date: Optional[str]
    uniform: Optional[int]
    position: str
    is_national: bool = False
    is_starter: bool = False
    is_inactive: bool = False


class RosterTeam(BaseModel):
    abbreviation: str
    team_id: int
    roster: List[RosterPlayer] = []


class RosterTeams(BaseModel):
    team_1: RosterTeam
    team_2: RosterTeam


class Rosters(BaseModel):
    teams: RosterTeams


class Penalty(BaseModel):
    play_id: int
    play_sequence: int
    quarter: int
    play_clock_start: str
    play_clock_start_in_secs: int
    play_summary: str
    field_position_start: str
    field_position_end: str
    down: int
    yards_to_go: int
    penalty_id: int
    penalty_code: str
    penalty_name: str
    penalty_type_id: int
    penalty_type_name: str
    penalty_situation_id: int
    penalty_situation_code: str
    penalty_situation_name: str
    is_major: int
    was_accepted: int
    team_or_player_penalty: str
    team_abbreviation: str
    team_id: int
    game_id: int
    cfl_central_id: int
    first_name: str
    middle_name: str
    last_name: str


class PlayReview(BaseModel):
    play_id: int
    quarter: int
    play_clock_start: str
    play_clock_start_in_secs: int
    play_summary: str
    field_position_start: str
    field_position_end: str
    down: int
    yards_to_go: int
    play_type_id: int
    play_type_description: str
    play_review_type_id: int
    play_review_type_name: str
    play_reversed_on_review: bool
    game_id: int


class Game(BaseModel):
    game_id: str
    date_start: str
    # game_number: int
    week: int
    season: int
    # attendance: int
    # game_duration: Optional[int]
    event_type: EventType
    event_status: EventStatus
    # venue: Venue
    # weather: Weather
    # coin_toss: CoinToss
    # tickets_url: str
    team_1: Team
    team_2: Team
    boxscore: Optional[Boxscore]
    play_by_play: Optional[List[Play]]
    rosters: Optional[Rosters]
    penalties: Optional[List[Penalty]]
    play_reviews: Optional[List[PlayReview]]

    @staticmethod
    def get_game_id(year: int, week: int, game_number: int) -> str:
        return f"{year}{week:0>2}{game_number:0>2}"

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def hash(self) -> str:
        return hashlib.md5(json.dumps(self.json()).encode("utf-8")).hexdigest()
