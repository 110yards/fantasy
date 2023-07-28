from typing import Dict

from app.domain.enums.league_command_type import LeagueCommandType
from pydantic import BaseModel


class LeagueCommandPushData(BaseModel):
    command_type: LeagueCommandType
    command_data: Dict
