from api.app.domain.enums.login_type import LoginType
from typing import List, Optional
from api.app.core.base_entity import BaseEntity
from api.app.core.annotate_args import annotate_args
from datetime import datetime


@annotate_args
class User(BaseEntity):
    display_name: str
    email: str  # optional?
    login_type: LoginType
    social_id: Optional[str]
    last_sign_in: Optional[datetime]
    confirmed: bool = False
    commissioner_of: List[str] = []
