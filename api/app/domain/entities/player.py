from api.app.domain.entities.player_score import PlayerScore
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
class PlayerGameStats(Stats):
    team: Optional[Team]


@annotate_args
class Player(BaseEntity):
    stats_inc_id: Optional[str]
    cfl_central_id: int
    first_name: str
    last_name: str
    display_name: Optional[str]
    uniform: Optional[str]
    position: PositionType
    height_inches: Optional[str]
    weight_pounds: Optional[str]
    team: Team
    status_current: int
    birth_birthDate_full: Optional[str]
    birth_city: Optional[str]
    birth_state_abbreviation: Optional[str]
    birth_country_name: Optional[str]
    college_fullName: Optional[str]
    twitter: Optional[str]
    facebook: Optional[str]
    instagram: Optional[str]
    vine: Optional[str]
    custom_fields: Optional[str]
    national_status: Optional[str]
    profile_image_url: Optional[str]
    profile_image_circ_url: Optional[str]

    game_scores: Optional[Dict[str, PlayerScore]]
    season_score: Optional[PlayerScore]

    game_stats: Optional[Dict[str, PlayerGameStats]]
    season_stats: Stats = Stats()
    hash: str = ""

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


def from_cfl(player: dict) -> Player:
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
