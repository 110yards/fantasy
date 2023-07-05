from typing import Optional

import requests
from fastapi import Depends
from strivelogger import StriveLogger

from app.config.settings import Settings, get_settings
from app.domain.models.boxscore import (
    Boxscore,
    BoxscorePlayer,
    PlayerDefence,
    PlayerFieldGoals,
    PlayerOnePointConverts,
    PlayerPassing,
    PlayerStats,
    StatsCollection,
)
from app.domain.models.player import Player
from app.domain.store.player_store import PlayerStore, create_player_store

from ..models.name_slug import name_slug, name_slug_for_player
from ..models.scoreboard import ScoreboardGame
from ..store.scoreboard_store import ScoreboardStore, create_scoreboard_store


class ActiveBoxscoresService:
    def __init__(
        self,
        settings: Settings,
        player_store: PlayerStore,
        scoreboard_store: ScoreboardStore,
    ):
        self.settings = settings
        self.player_store = player_store
        self.scoreboard_store = scoreboard_store

    def get_boxscores(self) -> list[Boxscore]:
        scoreboard = self.scoreboard_store.get_scoreboard()

        if not scoreboard:
            StriveLogger.error("No scoreboard found in store")
            return []

        active_games = [g for g in scoreboard.games if g.is_active()]

        if active_games:
            StriveLogger.info(f"Found {len(active_games)} active games")
        else:
            StriveLogger.info("No active games found")
            return []

        boxscores = []

        for game in active_games:
            boxscore = self.load_boxscore(game)
            if boxscore:
                boxscores.append(boxscore)

        return boxscores

    def load_boxscore(self, game: ScoreboardGame) -> Optional[Boxscore]:
        url = self.settings.realtime_boxscore_url_format.format(game_id=game.realtime_source_id)

        StriveLogger.info(f"Loading realtime boxscore: {url}")
        response = requests.get(url)

        if response.status_code != 200:
            StriveLogger.error(f"Failed to load realtime boxscore: {response.status_code}")
            return None

        game_data = response.json()

        if not game_data:
            StriveLogger.warn("Failed to load realtime boxscore: no data")
            return None

        game_data = game_data.get("data")

        if not game_data.get("playerStats"):
            return None

        away_players = self.player_store.get_player_by_team(game.away_abbr)
        home_players = self.player_store.get_player_by_team(game.home_abbr)

        away_players = {name_slug_for_player(p): p for p in away_players.values() if p}
        home_players = {name_slug_for_player(p): p for p in home_players.values() if p}

        boxscore = Boxscore(
            source="realtime",
            game_id=game.game_id,
            away_abbr=game.away_abbr,
            home_abbr=game.home_abbr,
            player_stats=StatsCollection(),
            unmatched_player_stats=StatsCollection(),
        )

        self.fill_player_stats(boxscore, game.away_abbr, game_data["playerStats"]["awayTeam"], away_players)
        self.fill_player_stats(boxscore, game.home_abbr, game_data["playerStats"]["homeTeam"], home_players)

        return boxscore

    def fill_player_stats(self, boxscore: Boxscore, team_abbr: str, player_data: dict, players: dict[str, Player]):
        self.map_passing(boxscore, player_data["passing"], team_abbr, players)
        self.map_rushing(boxscore, player_data["rushing"], team_abbr, players)
        self.map_receiving(boxscore, player_data["receiving"], team_abbr, players)
        self.map_punts(boxscore, player_data["punts"], team_abbr, players)
        self.map_punt_returns(boxscore, player_data["puntReturns"], team_abbr, players)
        self.map_kick_returns(boxscore, player_data["kickoffReturns"], team_abbr, players)
        self.map_field_goals(boxscore, player_data["fieldGoals"], team_abbr, players)
        self.map_one_point_converts(boxscore, player_data["fieldGoals"], team_abbr, players)
        self.map_defence(boxscore, player_data["defence"], team_abbr, players)
        # # field_goal_returns=
        # # kicking=map_kicking(team_player_data["kicking"]),

    def _get_player(
        self,
        name: str,
        team_abbr: str,
        players: dict[str, Player],
        boxscore: Boxscore,
    ) -> Optional[PlayerStats]:
        slug = name_slug(team_abbr, name)
        player = players.get(slug)

        if player:
            player_stats = boxscore.player_stats.get(player.player_id)

            if player_stats:
                return player_stats
            else:
                boxscore_player = BoxscorePlayer(first_name=player.first_name, last_name=player.last_name, player_id=player.player_id, team_abbr=team_abbr)
                player_stats = PlayerStats(player=boxscore_player)
                boxscore.player_stats[player.player_id] = player_stats
                return player_stats
        else:
            StriveLogger.warn(f"Failed to match player {slug}")
            if slug not in boxscore.unmatched_player_stats:
                boxscore.unmatched_player_stats[slug] = PlayerStats(player=BoxscorePlayer(first_name=name, last_name=name, team_abbr=team_abbr))
            return boxscore.unmatched_player_stats[slug]

    def map_passing(self, boxscore: Boxscore, passing_data: dict, team_abbr: str, players: dict[str, Player]) -> PlayerPassing:
        passing: list[PlayerPassing] = []

        for player_data in passing_data if passing_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data["name"], team_abbr, players, boxscore)

            if not player:
                continue

            completion_attempts = stats["COMPLETIONS_ATTEMPTS"]["statValue"].split("/")

            if len(completion_attempts) != 2:
                StriveLogger.warn(f"Failed to parse completion attempts for {player.first_name} {player.last_name}")
                continue

            player.pass_attempts = int(completion_attempts[1])
            player.pass_completions = int(completion_attempts[0])
            player.pass_net_yards = int(stats["YARDS"]["statValue"])
            player.pass_touchdowns = int(stats["TOUCHDOWNS"]["statValue"])
            player.pass_interceptions = int(stats["INTERCEPTIONS"]["statValue"])

        return passing

    def map_rushing(self, boxscore: Boxscore, rushing_data: dict, team_abbr: str, players: dict[str, Player]):
        for player_data in rushing_data if rushing_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data["name"], team_abbr, players, boxscore)

            if not player:
                continue

            player.rush_attempts = int(stats["CARRIES"]["statValue"])
            player.rush_net_yards = int(stats["YARDS"]["statValue"])
            player.rush_touchdowns = int(stats["TOUCHDOWNS"]["statValue"])

    def map_receiving(self, boxscore: Boxscore, receiving_data: dict, team_abbr: str, players: dict[str, Player]):
        for player_data in receiving_data if receiving_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data["name"], team_abbr, players, boxscore)

            if not player:
                continue

            player.receive_caught = int(stats["RECEPTIONS"]["statValue"])
            player.receive_yards = int(stats["YARDS"]["statValue"])
            player.receive_touchdowns = int(stats["TOUCHDOWNS"]["statValue"])
            player.receive_long = 0  # missing

    def map_punts(self, boxscore: Boxscore, punting_data: dict, team_abbr: str, players: dict[str, Player]):
        for player_data in punting_data if punting_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data["name"], team_abbr, players, boxscore)

            if not player:
                continue

            player.punts = int(stats["PUNTING_NO"]["statValue"])
            player.punt_yards = int(stats["PUNTING_YDS"]["statValue"])
            player.punt_long = int(stats["PUNTING_LNG"]["statValue"])

    def map_punt_returns(self, boxscore: Boxscore, punt_return_data: dict, team_abbr: str, players: dict[str, Player]):
        for player_data in punt_return_data:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data["name"], team_abbr, players, boxscore)

            if not player:
                continue

            player.punt_returns = int(stats["PUNTRETURN_NO"]["statValue"])
            player.punt_returns_yards = int(stats["PUNTRETURN_YDS"]["statValue"])
            player.punt_returns_touchdowns = 0  # ack no touchdowns?!?)
            player.punt_returns_long = int(stats["PUNTRETURN_LNG"]["statValue"])

    def map_kick_returns(self, boxscore: Boxscore, kick_return_data: dict, team_abbr: str, players: dict[str, Player]):
        for player_data in kick_return_data:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data["name"], team_abbr, players, boxscore)

            if not player:
                continue

            player.kick_returns = int(stats["KICKRETURN_NO"]["statValue"])
            player.kick_returns_yards = int(stats["KICKRETURN_YDS"]["statValue"])
            player.kick_returns_touchdowns = 0  # ack, no touchdowns?!?
            player.kick_returns_long = int(stats["KICKRETURN_LNG"]["statValue"])

    def map_field_goals(self, boxscore: Boxscore, kicking_data: dict, team_abbr: str, players: dict[str, Player]):
        field_goals: list[PlayerFieldGoals] = []

        for player_data in kicking_data if kicking_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}

            if not stats.get("FIELDGOALS_FGFGA"):  # source mixes field goals and singles into this data
                continue

            player = self._get_player(player_data["name"], team_abbr, players, boxscore)

            if not player:
                continue

            success_attempts = stats["FIELDGOALS_FGFGA"]["statValue"].split("/")

            if len(success_attempts) != 2:
                StriveLogger.warn(f"Failed to parse field goal attempts for {player.player.first_name} {player.player.last_name}")
                continue

            player.field_goal_attempts = int(success_attempts[1])
            player.field_goal_made = int(success_attempts[0])
            # have blocked here

        return field_goals

    def map_one_point_converts(self, boxscore: Boxscore, one_point_convert_data: dict, team_abbr: str, players: dict[str, Player]) -> PlayerOnePointConverts:
        one_point_converts: list[PlayerOnePointConverts] = []

        for player_data in one_point_convert_data if one_point_convert_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}

            if not stats.get("FIELDGOALS_XP"):  # source mixes field goals and singles into this data
                continue

            player = self._get_player(player_data["name"], team_abbr, players, boxscore)

            if not player:
                continue

            player.one_point_converts_attempts = 0  # attempts missing
            player.one_point_converts_made = int(stats["FIELDGOALS_XP"]["statValue"])

        return one_point_converts

    def map_defence(self, boxscore: Boxscore, defence_data: dict, team_abbr: str, players: dict[str, Player]):
        defence: list[PlayerDefence] = []

        for player_data in defence_data if defence_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data["name"], team_abbr, players, boxscore)

            if not player:
                continue

            player.fumbles_forced = int(stats.get("DEFENCE_FF")["statValue"]) if stats.get("DEFENCE_FF") else 0
            player.interceptions = int(stats.get("DEFENCE_INT")["statValue"]) if stats.get("DEFENCE_INT") else 0
            player.sacks_qb_made = int(stats.get("DEFENCE_SK")["statValue"]) if stats.get("DEFENCE_SK") else 0
            player.tackles_defensive = int(stats.get("DEFENCE_SOLO")["statValue"]) if stats.get("DEFENCE_TKL") else 0
            player.passes_knocked_down = 0  # missing :(
            # have tackles for loss here

        return defence


def create_active_boxscores_service(
    settings: Settings = Depends(get_settings),
    player_store: PlayerStore = Depends(create_player_store),
    scoreboard_store: ScoreboardStore = Depends(create_scoreboard_store),
) -> ActiveBoxscoresService:
    return ActiveBoxscoresService(
        settings=settings,
        player_store=player_store,
        scoreboard_store=scoreboard_store,
    )
