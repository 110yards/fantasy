from datetime import datetime
from typing import List, Optional

from app.yards_py.core.annotate_args import annotate_args
from app.yards_py.core.base_entity import BaseEntity
from app.yards_py.domain.enums.login_type import LoginType



class User(BaseEntity):
    display_name: str
    email: str  # optional?
    login_type: LoginType
    social_id: Optional[str]
    last_sign_in: Optional[datetime]
    confirmed: bool = False
    commissioner_of: List[str] = []
    is_admin: bool = False
    is_mod: bool = False
