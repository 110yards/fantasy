from typing import Dict
from pydantic import BaseModel
from api.app.core.annotate_args import annotate_args
from api.app.domain.enums.league_command_type import LeagueCommandType


@annotate_args
class LeagueCommandPushData(BaseModel):
    command_type: LeagueCommandType
    command_data: Dict
