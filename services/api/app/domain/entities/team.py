from __future__ import annotations

from typing import Dict, Optional

from pydantic import BaseModel

from app.core.exceptions import ApiException


class Team(BaseModel):
    id: int
    location: str
    name: str
    abbreviation: str
    roster_id: Optional[int] = None

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
        team = next((team for team in Team.all() if team.id == id), None)
        if not team:
            raise ApiException(f"Invalid team id '{id}'")

        return team

    @staticmethod
    def by_abbreviation(abbreviation: str):
        if not abbreviation:
            raise ApiException("Abbreviation must not be None")

        team = next((team for team in Team.all() if team.abbreviation == abbreviation.upper()), None)
        if not team:
            raise ApiException(f"Invalid team '{abbreviation}'")

        return team

    @staticmethod
    def from_cfl_api(input: Dict) -> Team:
        if not input["is_set"]:
            return Team.free_agent()
        else:
            abbreviation = input["abbreviation"]
            return Team.by_abbreviation(abbreviation)

    @staticmethod
    def free_agent():
        return Team(id=0, abbreviation="FA", location="Free", name="Agent")

    @staticmethod
    def bc():
        return Team(id=1, abbreviation="BC", location="BC", name="Lions", roster_id=5608)

    @staticmethod
    def cgy():
        return Team(id=2, abbreviation="CGY", location="Calgary", name="Stampeders", roster_id=5609)

    @staticmethod
    def edm():
        return Team(id=3, abbreviation="EDM", location="Edmonton", name="Elks", roster_id=5610)

    @staticmethod
    def ham():
        return Team(id=4, abbreviation="HAM", location="Hamilton", name="Tiger-Cats", roster_id=5611)

    @staticmethod
    def mtl():
        return Team(id=5, abbreviation="MTL", location="Montreal", name="Alouettes", roster_id=5612)

    @staticmethod
    def ott():
        return Team(id=6, abbreviation="OTT", location="Ottawa", name="Redblacks", roster_id=27755)

    @staticmethod
    def ssk():
        return Team(id=7, abbreviation="SSK", location="Saskatchewan", name="Roughriders", roster_id=5614)

    @staticmethod
    def tor():
        return Team(id=8, abbreviation="TOR", location="Toronto", name="Argonauts", roster_id=5615)

    @staticmethod
    def wpg():
        return Team(id=9, abbreviation="WPG", location="Winnipeg", name="Blue Bombers", roster_id=5616)
