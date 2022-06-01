from __future__ import annotations

from api.app.domain.entities.player_game import PlayerGame
from api.app.domain.entities.stats import Stats
from typing import List
from api.app.core.base_entity import BaseEntity
from api.app.core.annotate_args import annotate_args


@annotate_args
class PlayerSeason(BaseEntity):
    season: int
    games_played: int
    player_id: str
    stats: Stats
    games: List[PlayerGame] = []

    @staticmethod
    def create(season: int, player_id: str, player_games: List[PlayerGame]):
        stats = Stats()

        for player_game in player_games:
            for key in player_game.stats.dict():
                game_total = getattr(player_game.stats, key)
                if game_total is None:
                    continue

                season_total = getattr(stats, key)

                if season_total is None:
                    season_total = 0

                season_total += game_total
                setattr(stats, key, season_total)

        id = f"{player_id}"
        games_played = len(player_games)
        player_season = PlayerSeason(id=id, player_id=player_id, season=season, stats=stats, games_played=games_played, games=player_games)
        player_season.calculate_hash()

        return player_season
