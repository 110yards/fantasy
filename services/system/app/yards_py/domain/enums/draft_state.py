from enum import Enum


class DraftState(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "completed"
    RESET = "reset"
