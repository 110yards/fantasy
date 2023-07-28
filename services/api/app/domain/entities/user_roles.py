from typing import List

from app.core.annotate_args import annotate_args
from app.core.base_entity import BaseEntity
from app.core.role import Role


@annotate_args
class UserRoles(BaseEntity):
    roles: List[Role] = []
