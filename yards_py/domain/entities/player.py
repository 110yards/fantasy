from __future__ import annotations
from datetime import datetime

from pydantic.class_validators import root_validator
from yards_py.domain.entities.game_player import GamePlayer
from yards_py.domain.entities.injury_status import InjuryStatus
from yards_py.domain.enums.position_type import PositionType
from yards_py.core.hash_dict import hash_dict
from typing import Dict, Optional
from yards_py.core.base_entity import BaseEntity
from .team import Team
from yards_py.core.annotate_args import annotate_args

STATUS_INACTIVE = 0
STATUS_ACTIVE = 1


@annotate_args
class Player(BaseEntity):
    player_id: Optional[str]
    stats_inc_id: Optional[str]
    cfl_central_id: Optional[int]
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
    injury_status: Optional[InjuryStatus] = None

    hash: str = ""

    @property
    def national_status(self):
        return None if self.foreign_player else "N"

    @property
    def cfl_url(self) -> str:
        return f"https://www.cfl.ca/players/player/{self.id}"

    @property
    def formatted_height(self) -> str:
        if not self.height:
            return None

        try:
            ft = int(float(self.height))
            inches = int(self.height.split(".")[1])
        except BaseException:
            return None

        return f"{ft}'{inches}"

    @property
    def formatted_weight(self) -> str:
        if not self.weight:
            return None

        return f"{self.weight} lbs"

    @property
    def age(self) -> int:
        if not self.birth_date:
            return None

        try:
            birth_date = datetime.strptime(self.birth_date, "%Y-%m-%d")
            return int((datetime.now() - birth_date).days / 365.25)
        except ValueError:
            return None

    def compute_hash(self):
        self.hash = hash_dict(self.dict())

    @staticmethod
    def from_cfl_api(input: Dict, official_api: bool) -> Player:
        uniform = input["team"].get("uniform", None)
        input["team"] = Team.from_cfl_api(input["team"])
        input["position"] = PositionType.from_cfl_roster(input["position"]["abbreviation"])
        input["last_name"] = input["last_name"].title()

        player = Player(**input)
        player.id = str(player.cfl_central_id) if official_api else player.player_id
        assert player.id is not None, "Player id is none"
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
