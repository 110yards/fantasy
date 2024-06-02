from __future__ import annotations


from typing import Dict, List, Literal, Optional
from yards_py.domain.entities.game_status import GameStatus
from pydantic.main import BaseModel
from yards_py.core.base_entity import BaseEntity
from datetime import datetime

from .season_schedule import ScheduleGame

from .team import Team

POSTPONED_IS_CANCELLED_AFTER_HOURS = 24


class ScoreboardGame(BaseModel):
    year: int
    week: int
    game_id: str
    date_start: datetime
    away: Team
    home: Team
    away_score: int
    home_score: int
    game_status: GameStatus
    winner: Literal["home", "away", "tie", "no_result"]


    @staticmethod
    def create_from_game(game: ScheduleGame) -> ScoreboardGame:
        return ScoreboardGame(
            year=game.year,
            week=game.week,
            game_id=game.game_id,
            date_start=game.date_start,
            game_status=GameStatus.create_pre_game(),
            away=game.away,
            home=game.home,
            away_score=0,
            home_score=0,
            winner="no_result",        
        )
    
    def has_started(self) -> bool:
        return self.game_status.has_started

    def is_complete(self) -> bool:
        return self.game_status.is_final


class Scoreboard(BaseEntity):
    games: Dict[str, ScoreboardGame]
    id = "scoreboard"

    def all_games_complete(self) -> bool:
        unfinished_games = [game for game in self.games.values() if not game.is_complete()]

        return len(unfinished_games) == 0

    def last_game_start_time(self) -> datetime:
        start_times = [game.date_start for game in self.games.values()]
        last_start = max(start_times)
        return last_start

    def get_game_for_team(self, team_abbr) -> Optional[ScoreboardGame]:
        game = next(
            (game for game in self.games.values()
             if (game.away and game.away.abbr == team_abbr) or (game.home and game.home.abbr == team_abbr)), None)

        return game

    def week(self) -> bool:
        game_weeks = set(game.week for game in self.games.values())
        return max(game_weeks)


    @staticmethod
    def create(games: List[ScheduleGame]) -> Scoreboard:
        scoreboard_games: List[ScoreboardGame] = []
        for game in games:
            scoreboard_game = ScoreboardGame.create_from_game(game)
            scoreboard_games.append(scoreboard_game)

        scoreboard_games = {game.game_id: game for game in scoreboard_games}

        return Scoreboard(games=scoreboard_games)

