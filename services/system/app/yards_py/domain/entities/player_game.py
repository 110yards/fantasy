from __future__ import annotations

from datetime import datetime
from typing import Literal

from app.yards_py.domain.entities.stats import Stats
from pydantic import BaseModel

from .boxscore import BoxscoreGame


class GameResult(BaseModel):
    team_abbr: str
    opponent_abbr: str
    score_for: int
    score_against: int
    result: Literal["W", "L", "T"]
    was_home: bool
    game_date: datetime

    @staticmethod
    def create(boxscore_game: BoxscoreGame, player_team_abbr: str) -> GameResult:
        was_home = player_team_abbr == boxscore_game.home_abbr
        score_for = boxscore_game.home_score if was_home else boxscore_game.away_score
        score_against = boxscore_game.away_score if was_home else boxscore_game.home_score
        result = "W" if score_for > score_against else "L" if score_for < score_against else "T"
        team_abbr = boxscore_game.home_abbr if was_home else boxscore_game.away_abbr
        opponent_abbr = boxscore_game.away_abbr if was_home else boxscore_game.home_abbr

        return GameResult(
            game_date=boxscore_game.game_date,
            score_for=score_for,
            score_against=score_against,
            result=result,
            was_home=was_home,
            team_abbr=team_abbr,
            opponent_abbr=opponent_abbr,
        )


class PlayerGame(BaseModel):
    player_id: str
    game_id: str
    week_number: int
    stats: Stats
    game_result: GameResult
