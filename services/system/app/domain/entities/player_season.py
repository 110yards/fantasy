from __future__ import annotations

from typing import List

from app.yards_py.core.base_entity import BaseEntity
from app.yards_py.domain.entities.player_game import PlayerGame
from app.yards_py.domain.entities.stats import Stats
from pydantic import computed_field


class PlayerSeason(BaseEntity):
    season: int
    player_id: str
    stats: Stats
    games: List[PlayerGame] = []

    @computed_field
    @property
    def games_played(self) -> int:
        return len(self.games)

    @staticmethod
    def create(season: int, player_id: str, player_games: List[PlayerGame]):
        id = f"{player_id}"
        player_season = PlayerSeason(id=id, player_id=player_id, season=season, stats=Stats(), games=player_games)
        player_season.recalc_stats()

        return player_season

    def add_game(self, game: PlayerGame):
        # find next game by game id
        existing_game = next((g for g in self.games if g.game_id == game.game_id), None)
        if existing_game:
            self.games.remove(existing_game)

        self.games.append(game)
        self.recalc_stats()

    def recalc_stats(self):
        stats = Stats()

        for game in self.games:
            for key in game.stats.model_dump():
                game_total = getattr(game.stats, key)
                if game_total is None:
                    continue

                season_total = getattr(stats, key)

                if season_total is None:
                    season_total = 0

                season_total += game_total
                setattr(stats, key, season_total)

        self.stats = stats
