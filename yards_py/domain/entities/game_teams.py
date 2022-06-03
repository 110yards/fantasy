from pydantic import BaseModel

from .team import Team


class GameTeams(BaseModel):
    away: Team
    home: Team
