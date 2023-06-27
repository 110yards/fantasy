# import hashlib
# import json
# from enum import Enum

# from pydantic import BaseModel

# from app.domain.models.player import Team


# class InjuryStatus(str, Enum):
#     Probable = "probable"
#     Questionable = "questionable"
#     Out = "out"
#     InjuredSixGames = "six-game"


# class InjuryDetails(BaseModel):
#     status_id: InjuryStatus
#     text: str
#     last_updated: str
#     injury: str


# class InjuryPlayer(BaseModel):
#     first_name: str
#     last_name: str
#     team: Team
#     player_id: str


# class PlayerInjuryStatus(BaseModel):
#     player: InjuryPlayer
#     status: InjuryDetails


# class InjuryReport(BaseModel):
#     reports: list[PlayerInjuryStatus]

#     def hash(self) -> str:
#         return hashlib.md5(json.dumps(self.json()).encode("utf-8")).hexdigest()
