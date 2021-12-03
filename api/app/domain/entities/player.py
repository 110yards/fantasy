from __future__ import annotations

from pydantic.class_validators import root_validator
from api.app.domain.entities.game_player import GamePlayer
from api.app.domain.enums.position_type import PositionType
from api.app.domain.entities.stats import Stats
from api.app.core.hash_dict import hash_dict
from typing import Dict, Optional
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
    status_current: Optional[int]
    birth_date: Optional[str]
    birth_place: Optional[str]
    college: Optional[str]
    foreign_player: Optional[bool]
    image_url: Optional[str]

    season_stats: Stats = Stats()
    hash: str = ""

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

    def recalc_season_stats(self):
        for stat_key in self.season_stats.dict():
            setattr(self.season_stats, stat_key, 0)

        season_total = 0
        if self.game_stats:
            for game_id in self.game_stats:
                game = self.game_stats[game_id]
                for key in game.dict():
                    game_total = getattr(game, key)
                    if game_total is None:
                        continue

                    season_total = getattr(self.season_stats, key, None)

                    if season_total is not None:
                        season_total += game_total
                        setattr(self.season_stats, key, season_total)


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
