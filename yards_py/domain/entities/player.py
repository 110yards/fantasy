from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field
from pydantic.class_validators import root_validator

from yards_py.core.annotate_args import annotate_args
from yards_py.core.base_entity import BaseEntity
from yards_py.core.hash_dict import hash_dict
from yards_py.domain.entities.game_player import GamePlayer
from yards_py.domain.entities.injury_status import InjuryStatus
from yards_py.domain.enums.position_type import PositionType

from .team import Team

STATUS_INACTIVE = 0
STATUS_ACTIVE = 1


class PlayerPosition(str, Enum):
    qb = "qb"
    rb = "rb"
    wr = "wr"
    k = "k"
    lb = "lb"
    dl = "dl"
    db = "db"
    unknown = "unknown"

    @staticmethod
    def from_core(position_id: str) -> PlayerPosition:
        match position_id:
            case "qb":
                return PlayerPosition.qb
            case "rb" | "fb":
                return PlayerPosition.rb
            case "wr" | "te":
                return PlayerPosition.wr
            case "k" | "p":
                return PlayerPosition.k
            case "lb":
                return PlayerPosition.lb
            case "dl":
                return PlayerPosition.dl
            case "db" | "s":
                return PlayerPosition.db
            case _:
                return PlayerPosition.unknown


class Player(BaseEntity):
    player_id: str | None
    source_id: str | None
    first_name: str
    last_name: str
    uniform: str | None
    position: PlayerPosition
    height: str | None
    weight: int | None
    team: Team
    birth_date: datetime | None
    birth_place: str | None
    school: str | None
    canadian_player: bool
    injury_status: InjuryStatus | None = None

    hash: str = ""

    @property
    def display_name(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else None

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
            return int((datetime.now(tz=timezone.utc) - self.birth_date).days / 365.25)
        except ValueError:
            return None

    def compute_hash(self):
        self.hash = hash_dict(self.dict())

    @staticmethod
    def from_core(data: dict) -> Player:
        position = data.pop("position")
        position_id = position.get("id") if position else None
        player_id = data.get("player_id")

        position = PlayerPosition.from_core(position_id)

        return Player(id=player_id, position=position, **data)


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
