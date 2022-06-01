from typing import List
from api.app.core.base_entity import BaseEntity
from api.app.core.annotate_args import annotate_args
from api.app.core.role import Role


@annotate_args
class UserRoles(BaseEntity):
    roles: List[Role] = []
