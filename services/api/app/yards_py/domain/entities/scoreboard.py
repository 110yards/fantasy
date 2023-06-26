from __future__ import annotations

import pytz

from app.yards_py.domain.entities.game import Game
from typing import Dict, List, Optional
from app.yards_py.domain.entities.game_teams import GameTeams
from app.yards_py.domain.entities.event_type import EventType
from app.yards_py.domain.entities.game_score import GameScore
from app.yards_py.domain.entities.event_status import EVENT_STATUS_CANCELLED, EVENT_STATUS_FINAL, EVENT_STATUS_POSTPONED, EventStatus
from pydantic.main import BaseModel
from app.yards_py.core.base_entity import BaseEntity
from app.yards_py.core.annotate_args import annotate_args
from datetime import datetime

POSTPONED_IS_CANCELLED_AFTER_HOURS = 24


@annotate_args
class ScoreboardGame(BaseModel):
    id: str
    date_start: datetime
    # game_number: int
    week: int
    season: int
    event_type: EventType
    event_status: EventStatus
    score: GameScore
    teams: GameTeams
    hash: Optional[str]

    @staticmethod
    def create_from_game(game: Game) -> ScoreboardGame:
        return ScoreboardGame(
            id=str(game.id),
            date_start=game.date_start,
            # game_number=game.game_number,
            week=game.week,
            season=game.season,
            event_type=game.event_type,
            event_status=game.event_status,
            score=game.score,
            teams=game.teams,
            hash=game.hash
        )

    def is_complete(self) -> bool:
        if self.event_status.event_status_id == EVENT_STATUS_POSTPONED:
            seconds_past_start = (datetime.now(tz=pytz.utc) - self.date_start).total_seconds()
            hours_past_start = seconds_past_start / 3600
            return hours_past_start >= POSTPONED_IS_CANCELLED_AFTER_HOURS

        complete_statuses = [EVENT_STATUS_FINAL, EVENT_STATUS_CANCELLED]

        return self.event_status.event_status_id in complete_statuses


@annotate_args
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

    def get_game_for_team(self, team_id) -> Optional[ScoreboardGame]:
        game = next(
            (game for game in self.games.values()
             if (game.teams.away and game.teams.away.id == team_id) or (game.teams.home and game.teams.home.id == team_id)), None)

        return game

    def week(self) -> bool:
        game_weeks = set(game.week for game in self.games.values())
        return max(game_weeks)

    def changed(self, other: Scoreboard) -> bool:
        if not other:
            return True

        for game in self.games.values():
            other_game = other.games.get(game.id, None)
            if not other_game:
                return True

            if game.hash != other_game.hash:
                return True

        return False

    @staticmethod
    def create(games: List[Game]) -> Scoreboard:
        scoreboard_games: List[ScoreboardGame] = []
        for game in games:
            scoreboard_game = ScoreboardGame.create_from_game(game)
            scoreboard_games.append(scoreboard_game)

        scoreboard_games = {game.id: game for game in scoreboard_games}

        return Scoreboard(games=scoreboard_games)
