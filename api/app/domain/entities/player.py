from __future__ import annotations
from pydantic import BaseModel

from pydantic.class_validators import root_validator
from api.app.domain.entities.game_player import GamePlayer
from api.app.domain.entities.player_score import PlayerScore
from api.app.domain.entities.scoring_settings import ScoringSettings
from api.app.domain.enums.position_type import PositionType
from api.app.domain.entities.stats import Stats
from api.app.core.hash_dict import hash_dict
from typing import Dict, List, Optional
from api.app.core.base_entity import BaseEntity
from .team import Team
from api.app.core.annotate_args import annotate_args

STATUS_INACTIVE = 0
STATUS_ACTIVE = 1


@annotate_args
class PlayerGame(BaseEntity):
    player_id: str
    game_id: int
    week_number: int
    team: Team
    opponent: Team
    stats: Stats


@annotate_args
class PlayerSeason(BaseEntity):
    season: int
    games_played: int
    player_id: str
    stats: Stats
    games: List[PlayerGame] = []

    @staticmethod
    def create(season: int, player_id: str, player_games: List[PlayerGame]):
        stats = Stats()

        for player_game in player_games:
            for key in player_game.stats.dict():
                game_total = getattr(player_game.stats, key)
                if game_total is None:
                    continue

                season_total = getattr(stats, key)

                if season_total is None:
                    season_total = 0

                season_total += game_total
                setattr(stats, key, season_total)

        id = f"{player_id}"
        games_played = len(player_games)
        return PlayerSeason(id=id, player_id=player_id, season=season, stats=stats, games_played=games_played, games=player_games)


class PlayerLeagueGameScore(BaseModel):
    game_id: str
    week_number: int
    team: Team
    opponent: Team
    score: PlayerScore


@annotate_args
class PlayerLeagueSeasonScore(BaseEntity):
    season: int
    player_id: str
    total_score: float
    average_score: float
    rank: Optional[int]
    game_scores: Dict[str, PlayerLeagueGameScore]

    @staticmethod
    def create(id: str, player_season: PlayerSeason, scoring: ScoringSettings) -> PlayerLeagueSeasonScore:
        score = scoring.calculate_score(player_season.stats)
        average = score.total_score / player_season.games_played if player_season.games_played else 0
        game_scores = {}

        for game in player_season.games:
            score = scoring.calculate_score(game.stats)
            game_score = PlayerLeagueGameScore(
                game_id=game.id,
                week_number=game.week_number,
                team=game.team,
                opponent=game.opponent,
                score=score,
            )
            game_scores[game.id] = game_score

        return PlayerLeagueSeasonScore(
            id=id,
            player_id=player_season.player_id,
            season=player_season.season,
            total_score=score.total_score,
            average_score=average,
            game_scores=game_scores
        )


@annotate_args
class Player(BaseEntity):
    stats_inc_id: Optional[str]
    cfl_central_id: int
    first_name: str
    last_name: str
    display_name: Optional[str]
    uniform: Optional[str]
    position: PositionType
    height: Optional[str]
    weight: Optional[int]
    team: Team
    birth_date: Optional[str]
    birth_place: Optional[str]
    college: Optional[str]
    foreign_player: Optional[bool]
    image_url: Optional[str]
    status_current: int = 1

    season_stats: Stats = Stats()
    hash: str = ""

    @property
    def national_status(self):
        return None if self.foreign_player else "N"

    def compute_hash(self):
        self.hash = hash_dict(self.dict())

    @staticmethod
    def from_cfl_api(input: Dict) -> Player:
        uniform = input["team"].get("uniform", None)
        input["team"] = Team.from_cfl_api(input["team"])
        input["position"] = PositionType.from_cfl_roster(input["position"]["abbreviation"])
        input["last_name"] = input["last_name"].title()

        player = Player.parse_obj(input)
        player.id = str(player.cfl_central_id)
        player.college = input.get("school", {}).get("name", None)
        player.uniform = uniform
        return player

    @root_validator
    def set_display_name(cls, values):
        if "first_name" in values and "last_name" in values:
            values["display_name"] = f"{values['first_name']} {values['last_name']}"
        return values


def from_team_roster(player: dict) -> Player:
    player["id"] = str(player["cfl_central_id"])
    player["stats_inc_id"] = player["playerId"]
    player["last_name"] = clean_name(player["lastName"])
    player["first_name"] = clean_name(player["firstName"])
    player["position"] = PositionType.from_cfl_roster(player["positions_1_abbreviation"])

    # there's a bug in their API....
    if player["team_location"] == "Edmonton" and player["team_abbreviation"] is None:
        player["team_abbreviation"] = "EDM"

    player["team"] = Team.by_abbreviation(player["team_abbreviation"])

    new_player = Player.parse_obj(player)
    new_player.hash = hash_dict(new_player.dict())
    return new_player


def clean_name(name: str):
    name = name.replace("&#39;", "'")

    return name


def from_game_player(player: GamePlayer, team: Team) -> Player:
    return Player(
        id=player.id,
        cfl_central_id=int(player.id),
        first_name=player.first_name,
        last_name=player.last_name,
        birth_date=player.birth_date,
        uniform=player.uniform,
        position=player.position.lower(),
        team=team,
        hash="",
        status_current=1,  # ???
        game_stats={},
    )
