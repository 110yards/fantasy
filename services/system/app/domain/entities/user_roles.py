from typing import List

from app.core.base_entity import BaseEntity
from app.core.role import Role


class UserRoles(BaseEntity):
    roles: List[Role] = []
