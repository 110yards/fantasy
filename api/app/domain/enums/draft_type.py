from enum import Enum


class DraftType(str, Enum):
    SNAKE = "snake"
    AUCTION = "auction"
    COMMISSONER = "commissioner"
