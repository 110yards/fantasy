from typing import Optional

import requests
from fastapi import Depends
from strivelogger import StriveLogger

from app.domain.models.boxscore import (
    Boxscore,
    BoxscoreGame,
    BoxscorePlayer,
    PlayerStats,
    StatsCollection,
)
from app.domain.store.player_store import PlayerStore, create_player_store

from ....config.settings import Settings, get_settings
from ...models.schedule import ScheduleGame
from ...models.scoreboard import ScoreboardGame
from ...store.schedule_store import ScheduleStore, create_schedule_store
from ...store.scoreboard_store import ScoreboardStore, create_scoreboard_store
from .boxscore_loader import BoxscoreLoader


class OfficialBoxscoreLoader(BoxscoreLoader):
    def __init__(
        self,
        settings: Settings,
        player_store: PlayerStore,
        scoreboard_store: ScoreboardStore,
        schedule_store: ScheduleStore,
    ):
        self.settings = settings
        self.player_store = player_store
        self.scoreboard_store = scoreboard_store
        self.schedule_store = schedule_store

    def load_boxscore(self, year: int, game: ScoreboardGame | ScheduleGame) -> Optional[Boxscore]:
        # boxscore_season_id = self.schedule_store.get_boxscore_source_season_id(year)

        # url = self.settings.boxscore_url_format.format(game_id=game.boxscore_source_id, season_id=boxscore_season_id)
        url = self.settings.boxscore_url_format.format(game_id=game.boxscore_source_id)

        StriveLogger.info(f"Loading official boxscore: {url}")
        response = requests.get(
            url,
            headers={
                "Referer": self.settings.boxscore_url_referer,
            },
        )

        if response.status_code != 200:
            StriveLogger.error(f"Failed to load official boxscore: {response.status_code}")
            return None

        game_data = response.json()

        if not game_data:
            StriveLogger.warn("Failed to load official boxscore: no data")
            return None

        game_data = game_data["scores"]

        if not game_data.get("matchPlayerStats"):
            StriveLogger.warn("Failed to load official boxscore: no player stats")
            return None

        game = BoxscoreGame(
            game_id=game.game_id,
            game_date=game.game_date if isinstance(game, ScoreboardGame) else game.date_start,
            away_abbr=game.away_abbr,
            home_abbr=game.home_abbr,
            away_score=game_data["awayResult"],
            home_score=game_data["homeResult"],
        )

        boxscore = Boxscore(
            source="official",
            game_id=game.game_id,
            game=game,
            away_abbr=game.away_abbr,
            home_abbr=game.home_abbr,
            player_stats=StatsCollection(),
            unmatched_player_stats=StatsCollection(),
        )

        self.fill_player_stats(boxscore, game.away_abbr, game_data["matchPlayerStats"][0]["awayTeamPlayers"])
        self.fill_player_stats(boxscore, game.home_abbr, game_data["matchPlayerStats"][0]["homeTeamPlayers"])

        return boxscore

    def fill_player_stats(self, boxscore: Boxscore, team_abbr: str, players_data: list[dict]):
        for player_data in players_data:
            player = self._get_player(player_data["playerId"], player_data["playerFirstName"], player_data["playerLastName"], team_abbr, boxscore)

            if not player:
                continue

            stats: dict = player_data["stats"]["gameStats"]

            player.pass_attempts = stats.get("passingPlaysAttempted", 0)
            player.pass_completions = stats.get("passingPlaysCompleted", 0)
            player.pass_net_yards = stats.get("passingYards", 0)
            player.pass_touchdowns = stats.get("passingTouchdowns", 0)
            player.pass_interceptions = stats.get("passingPlaysIntercepted", 0)
            player.rush_attempts = stats.get("rushingPlays", 0)
            player.rush_net_yards = stats.get("rushingNetYards", 0)
            player.rush_touchdowns = stats.get("rushingTouchdowns", 0)
            player.receive_caught = stats.get("receivingReceptions", 0)
            player.receive_yards = stats.get("receivingYards", 0)
            player.receive_touchdowns = stats.get("receivingTouchdowns", 0)
            player.receive_long = stats.get("receivingLongestYards", 0)
            player.punts = stats.get("puntingPlays", 0)
            player.punt_yards = stats.get("puntingGrossYards", 0)
            player.punt_net_yards = stats.get("puntingNetYards", 0)
            player.punt_long = stats.get("puntingLongestYards", 0)
            player.punt_returns = stats.get("puntReturns", 0)
            player.punt_returns_yards = stats.get("puntReturnYards", 0)
            player.punt_returns_touchdowns = stats.get("puntReturnTouchdowns", 0)
            player.punt_returns_long = stats.get("puntReturnLongestYards", 0)
            player.punt_singles = stats.get("puntSingles", 0)
            player.kicks_singles = stats.get("kickingSingles", 0)
            player.field_goal_returns = stats.get("missedFgReturns", 0)
            player.field_goal_returns_yards = stats.get("missedFgReturnYards", 0)
            player.field_goal_returns_touchdowns = stats.get("missedFgReturnTouchdowns", 0)
            player.field_goal_returns_long = stats.get("missedFgReturnsLongestYards", 0)
            player.kick_returns = stats.get("kickoffReturns", 0)
            player.kick_returns_yards = stats.get("kickoffReturnYards", 0)
            player.kick_returns_touchdowns = stats.get("kickoffReturnTouchdowns", 0)
            player.kick_returns_long = stats.get("kickoffReturnLongestYards", 0)
            player.field_goal_attempts = stats.get("fieldGoalsAttempted", 0)
            player.field_goal_made = stats.get("fieldGoalsSucceeded", 0)
            player.one_point_converts_attempts = stats.get("extraPointKicksAttempted", 0)
            player.one_point_converts_made = stats.get("extraPointKicksSucceeded", 0)
            player.fumbles_forced = stats.get("defenseForcedFumbles", 0)
            player.fumbles_recovered = stats.get("defenseFumblesRecovered", 0)
            player.interceptions = stats.get("defenseInterceptions", 0)
            player.sacks_qb_made = stats.get("defenseSacks", 0)
            player.tackles_defensive = stats.get("defenseTackles", 0)
            player.tackles_special_teams = stats.get("defenseSpecialTeamsTackles", 0)
            player.passes_knocked_down = 0  # missing
            player.tackles_for_loss = stats.get("defenseTacklesForLoss", 0)

            # TODO: fumbles lost / fumbles

    def _get_player(self, player_id: str, first_name: str, last_name: str, team_abbr: str, boxscore: Boxscore) -> Optional[PlayerStats]:
        player = self.player_store.get_player_by_boxscore_source_id(player_id)

        if player:
            boxscore_player = BoxscorePlayer(first_name=player.first_name, last_name=player.last_name, player_id=player.player_id, team_abbr=team_abbr)
            player_stats = PlayerStats(player=boxscore_player)
            boxscore.player_stats[player.player_id] = player_stats
            return player_stats
        else:
            StriveLogger.error(f"Failed to find player with boxscore id {player_id} in player store")
            key = player_id.replace("/", "").replace(":", "")
            boxscore.unmatched_player_stats[key] = PlayerStats(
                player=BoxscorePlayer(
                    first_name=first_name,
                    last_name=last_name,
                    player_id=player_id,
                    team_abbr=team_abbr,
                ),
            )
            return boxscore.unmatched_player_stats[key]


def create_official_boxscore_loader(
    settings: Settings = Depends(get_settings),
    player_store: PlayerStore = Depends(create_player_store),
    scoreboard_store: ScoreboardStore = Depends(create_scoreboard_store),
    schedule_store: ScheduleStore = Depends(create_schedule_store),
) -> OfficialBoxscoreLoader:
    return OfficialBoxscoreLoader(
        settings=settings,
        player_store=player_store,
        scoreboard_store=scoreboard_store,
        schedule_store=schedule_store,
    )
