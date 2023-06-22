from dataclasses import dataclass


@dataclass
class UpsertActiveGamesCommand:
    hours: int | None
