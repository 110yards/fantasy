from enum import Enum


class Role(str, Enum):
    admin = "ADMIN"
    mod = "MOD"
