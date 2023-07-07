from abc import ABC, abstractmethod
from typing import Optional

from app.domain.models.boxscore import (
    Boxscore,
)

from ...models.schedule import ScheduleGame
from ...models.scoreboard import ScoreboardGame


class BoxscoreLoader(ABC):
    @abstractmethod
    def load_boxscore(self, year: int, game: ScoreboardGame | ScheduleGame) -> Optional[Boxscore]:
        raise NotImplementedError()
