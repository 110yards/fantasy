from typing import Optional

from fastapi import Depends
from strivelogger import StriveLogger

from app.config.settings import Settings, get_settings
from app.domain.models.boxscore import (
    Boxscore,
)

from ..models.schedule import ScheduleGame
from ..models.scoreboard import ScoreboardGame
from ..store.schedule_store import ScheduleStore, create_schedule_store
from ..store.scoreboard_store import ScoreboardStore, create_scoreboard_store
from ..store.state_store import StateStore, create_state_store
from .boxscores.official_boxscore_loader import OfficialBoxscoreLoader, create_official_boxscore_loader


class FinalBoxscoresService:
    def __init__(
        self,
        settings: Settings,
        state_store: StateStore,
        scoreboard_store: ScoreboardStore,
        schedule_store: ScheduleStore,
        loader: OfficialBoxscoreLoader,
    ):
        self.settings = settings
        self.state_store = state_store
        self.scoreboard_store = scoreboard_store
        self.schedule_store = schedule_store
        self.loader = loader

    def get_boxscores(self, year: Optional[int] = None) -> list[Boxscore]:
        if year:
            games = self.get_all_games(year)
        else:
            games = self.get_current_games()

        boxscores = []
        for game in games:
            boxscore = self.loader.load_boxscore(year, game)
            if boxscore:
                boxscores.append(boxscore)

        return boxscores

    def get_current_games(self) -> list[ScoreboardGame]:
        scoreboard = self.scoreboard_store.get_scoreboard()

        if not scoreboard:
            StriveLogger.error("No scoreboard found in store")
            return []

        completed_games = [g for g in scoreboard.games if g.is_complete]

        if completed_games:
            StriveLogger.info(f"Found {len(completed_games)} completed games")
        else:
            StriveLogger.info("No completed games found")
            return []

    def get_all_games(self, year) -> list[ScheduleGame]:
        schedule = self.schedule_store.get_schedule(year)

        games = []
        for week in schedule.weeks.values():
            games.extend(week.games)

        return games


def create_final_boxscores_service(
    settings: Settings = Depends(get_settings),
    state_store: StateStore = Depends(create_state_store),
    scoreboard_store: ScoreboardStore = Depends(create_scoreboard_store),
    schedule_store: ScheduleStore = Depends(create_schedule_store),
    loader: OfficialBoxscoreLoader = Depends(create_official_boxscore_loader),
) -> FinalBoxscoresService:
    return FinalBoxscoresService(
        settings=settings,
        state_store=state_store,
        scoreboard_store=scoreboard_store,
        schedule_store=schedule_store,
        loader=loader,
    )
