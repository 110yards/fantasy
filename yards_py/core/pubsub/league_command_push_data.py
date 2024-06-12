from typing import Dict
from pydantic import BaseModel

from ...domain.enums.league_command_type import LeagueCommandType


class LeagueCommandPushData(BaseModel):
    command_type: LeagueCommandType
    command_data: Dict
