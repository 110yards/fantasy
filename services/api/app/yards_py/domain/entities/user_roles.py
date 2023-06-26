from typing import List
from app.yards_py.core.base_entity import BaseEntity
from app.yards_py.core.annotate_args import annotate_args
from app.yards_py.core.role import Role


@annotate_args
class UserRoles(BaseEntity):
    roles: List[Role] = []
