from __future__ import annotations

from pydantic import Field
from pydantic.main import BaseModel
from yards_py.core.exceptions import ApiException
from typing import Optional


class Team(BaseModel):
    location: str
    name: str
    abbr: str
    roster_id: Optional[int]

    @staticmethod
    def all():
        return [
            Team.bc(),
            Team.cgy(),
            Team.edm(),
            Team.ham(),
            Team.mtl(),
            Team.ott(),
            Team.ssk(),
            Team.tor(),
            Team.wpg(),
        ]

    @staticmethod
    def by_id(id):
        team = next((team for team in Team.all() if team.abbr == id), None)
        if not team:
            raise ApiException(f"Invalid team id '{id}'")

        return team

    @staticmethod
    def by_abbreviation(abbr: str):
        if not abbr:
            raise ApiException("abbr must not be None")
        
        if abbr == "FA":
            return Team.free_agent()

        team = next((team for team in Team.all() if team.abbr == abbr.upper()), None)
        if not team:
            raise ApiException(f"Invalid team '{abbr}'")

        return team

    @staticmethod
    def free_agent():
        return Team(id=0, abbr="FA", location="Free", name="Agent")

    @staticmethod
    def bc():
        return Team(id=1, abbr="BC", location="BC", name="Lions", roster_id=5608)

    @staticmethod
    def cgy():
        return Team(id=2, abbr="CGY", location="Calgary", name="Stampeders", roster_id=5609)

    @staticmethod
    def edm():
        return Team(id=3, abbr="EDM", location="Edmonton", name="Elks", roster_id=5610)

    @staticmethod
    def ham():
        return Team(id=4, abbr="HAM", location="Hamilton", name="Tiger-Cats", roster_id=5611)

    @staticmethod
    def mtl():
        return Team(id=5, abbr="MTL", location="Montreal", name="Alouettes", roster_id=5612)

    @staticmethod
    def ott():
        return Team(id=6, abbr="OTT", location="Ottawa", name="Redblacks", roster_id=27755)

    @staticmethod
    def ssk():
        return Team(id=7, abbr="SSK", location="Saskatchewan", name="Roughriders", roster_id=5614)

    @staticmethod
    def tor():
        return Team(id=8, abbr="TOR", location="Toronto", name="Argonauts", roster_id=5615)

    @staticmethod
    def wpg():
        return Team(id=9, abbr="WPG", location="Winnipeg", name="Blue Bombers", roster_id=5616)
