from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel


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
    player_id: str
    first_name: str
    last_name: str
    full_name: str
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

    hash: str = ""

    def likely_out_for_game(self) -> bool:
        if not self.injury_status:
            return False

        return self.injury_status.status_id in [InjuryStatus.Out, InjuryStatus.InjuredSixGames, InjuryStatus.Questionable]

    def is_free_agent(self) -> bool:
        return not self.team_abbr


#     @property
#     def cfl_url(self) -> str:
#         return f"https://www.cfl.ca/players/player/{self.id}"

#     @property
#     def formatted_height(self) -> str:
#         if not self.height:
#             return None

#         try:
#             ft = int(float(self.height))
#             inches = int(self.height.split(".")[1])
#         except BaseException:
#             return None

#         return f"{ft}'{inches}"

#     @property
#     def formatted_weight(self) -> str:
#         if not self.weight:
#             return None

#         return f"{self.weight} lbs"

#     @property
#     def age(self) -> int:
#         if not self.birth_date:
#             return None

#         try:
#             birth_date = datetime.strptime(self.birth_date, "%Y-%m-%d")
#             return int((datetime.now() - birth_date).days / 365.25)
#         except ValueError:
#             return None

#     def compute_hash(self):
#         self.hash = hash_dict(self.dict())

#     @staticmethod
#     def from_cfl_api(input: Dict, official_api: bool) -> Player:
#         uniform = input["team"].get("uniform", None)
#         input["team"] = Team.from_cfl_api(input["team"])
#         input["position"] = PositionType.from_cfl_roster(input["position"]["abbreviation"])
#         input["last_name"] = input["last_name"].title()

#         player = Player(**input)
#         player.player_id = str(player.cfl_central_id) if official_api else player.player_id
#         assert player.player_id is not None, "Player id is none"
#         player.college = input.get("school", {}).get("name", None)
#         player.uniform = uniform
#         return player

#     @root_validator
#     def set_display_name(cls, values):
#         if "first_name" in values and "last_name" in values:
#             values["display_name"] = f"{values['first_name']} {values['last_name']}"
#         return values


# def from_team_roster(player: dict) -> Player:
#     player["id"] = str(player["cfl_central_id"])
#     player["stats_inc_id"] = player["playerId"]
#     player["last_name"] = clean_name(player["lastName"])
#     player["first_name"] = clean_name(player["firstName"])
#     player["position"] = PositionType.from_cfl_roster(player["positions_1_abbreviation"])

#     # there's a bug in their API....
#     if player["team_location"] == "Edmonton" and player["team_abbreviation"] is None:
#         player["team_abbreviation"] = "EDM"

#     player["team"] = Team.by_abbreviation(player["team_abbreviation"])

#     new_player = Player.parse_obj(player)
#     new_player.hash = hash_dict(new_player.dict())
#     return new_player


# def clean_name(name: str):
#     name = name.replace("&#39;", "'")

#     return name


# def from_game_player(player: GamePlayer, team: Team) -> Player:
#     return Player(
#         id=player.player_id,
#         cfl_central_id=int(player.player_id),
#         first_name=player.first_name,
#         last_name=player.last_name,
#         birth_date=player.birth_date,
#         uniform=player.uniform,
#         position=player.position.lower(),
#         team=team,
#         hash="",
#         status_current=1,  # ???
#         game_stats={},
#     )
