from yards_py.core.base_entity import BaseEntity
from ..core.role import Role


class UserRoles(BaseEntity):
    roles: list[Role] = []
