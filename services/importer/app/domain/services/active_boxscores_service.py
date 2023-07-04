from typing import Optional

import requests
from fastapi import Depends
from strivelogger import StriveLogger

from app.config.settings import Settings, get_settings
from app.domain.models.boxscore import (
    Boxscore,
    BoxscorePlayer,
    BoxscoreTeam,
    PlayerDefence,
    PlayerFieldGoals,
    PlayerKickReturns,
    PlayerOnePointConverts,
    PlayerPassing,
    PlayerPuntReturns,
    PlayerPunts,
    PlayerReceiving,
    PlayerRushing,
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

        StriveLogger.warn(f"Loading CFL boxscore: {url}")
        response = requests.get(url)

        if response.status_code != 200:
            StriveLogger.error(f"Failed to load CFL boxscore: {response.status_code}")
            return None

        game_data = response.json()

        if not game_data:
            StriveLogger.warn("Failed to load CFL boxscore: no data")
            return None

        game_data = game_data["data"]

        if not game_data["playerStats"]:
            return None

        away_players = self.player_store.get_player_by_team(game.away_abbr)
        home_players = self.player_store.get_player_by_team(game.home_abbr)

        away_players = {name_slug_for_player(p): p for p in away_players.values() if p}
        home_players = {name_slug_for_player(p): p for p in home_players.values() if p}

        away_box = self.map_boxscore_team(game.away_abbr, game_data["playerStats"]["awayTeam"], away_players)
        home_box = self.map_boxscore_team(game.home_abbr, game_data["playerStats"]["homeTeam"], home_players)

        return Boxscore(
            away_abbr=game.away_abbr,
            away_box=away_box,
            home_abbr=game.home_abbr,
            home_box=home_box,
        )

    def map_boxscore_team(self, team_abbr: str, player_data: dict, players: dict[str, Player]) -> BoxscoreTeam:
        return BoxscoreTeam(
            passing=self.map_passing(player_data["passing"], team_abbr, players),
            rushing=self.map_rushing(player_data["rushing"], team_abbr, players),
            receiving=self.map_receiving(player_data["receiving"], team_abbr, players),
            punts=self.map_punts(player_data["punts"], team_abbr, players),
            punt_returns=self.map_punt_returns(player_data["puntReturns"], team_abbr, players),
            kick_returns=self.map_kick_returns(player_data["kickoffReturns"], team_abbr, players),
            field_goals=self.map_field_goals(player_data["fieldGoals"], team_abbr, players),
            # field_goal_returns=
            # kicking=map_kicking(team_player_data["kicking"]),
            one_point_converts=self.map_one_point_converts(player_data["fieldGoals"], team_abbr, players),
            defence=self.map_defence(player_data["defence"], team_abbr, players),
        )

    def _get_player(self, name: str, team_abbr: str, players: dict[str, Player]) -> Optional[BoxscorePlayer]:
        slug = name_slug(team_abbr, name)
        player = players.get(slug)

        if player:
            return BoxscorePlayer(
                first_name=player.first_name,
                last_name=player.last_name,
                player_id=player.player_id,
                birth_date=player.birth_date,
            )
        else:
            StriveLogger.warn(f"Failed to match player {slug}")
            return None

    def map_passing(self, passing_data: dict, team_abbr: str, players: dict[str, Player]) -> PlayerPassing:
        passing: list[PlayerPassing] = []

        for player_data in passing_data if passing_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data["name"], team_abbr, players)

            if not player:
                continue

            completion_attempts = stats["COMPLETIONS_ATTEMPTS"]["statValue"].split("/")

            if len(completion_attempts) != 2:
                StriveLogger.warn(f"Failed to parse completion attempts for {player.first_name} {player.last_name}")
                continue

            passing.append(
                PlayerPassing(
                    player=player,
                    pass_attempts=completion_attempts[1],
                    pass_completions=completion_attempts[0],
                    pass_net_yards=stats["YARDS"]["statValue"],
                    pass_touchdowns=stats["TOUCHDOWNS"]["statValue"],
                    pass_interceptions=stats["INTERCEPTIONS"]["statValue"],
                )
            )

        return passing

    def map_rushing(self, rushing_data: dict, team_abbr: str, players: dict[str, Player]) -> PlayerRushing:
        rushing: list[PlayerRushing] = []

        for player_data in rushing_data if rushing_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data["name"], team_abbr, players)

            if not player:
                continue

            rushing.append(
                PlayerRushing(
                    player=player,
                    rush_attempts=stats["CARRIES"]["statValue"],
                    rush_net_yards=stats["YARDS"]["statValue"],
                    rush_touchdowns=stats["TOUCHDOWNS"]["statValue"],
                )
            )

        return rushing

    def map_receiving(self, receiving_data: dict, team_abbr: str, players: dict[str, Player]) -> PlayerReceiving:
        receiving: list[PlayerReceiving] = []

        for player_data in receiving_data if receiving_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data["name"], team_abbr, players)

            if not player:
                continue

            receiving.append(
                PlayerReceiving(
                    player=player,
                    receive_caught=stats["RECEPTIONS"]["statValue"],
                    receive_yards=stats["YARDS"]["statValue"],
                    receive_touchdowns=stats["TOUCHDOWNS"]["statValue"],
                    receive_long=0,  # missing
                )
            )

        return receiving

    def map_punts(self, punting_data: dict, team_abbr: str, players: dict[str, Player]) -> PlayerPunts:
        punting: list[PlayerPunts] = []

        for player_data in punting_data if punting_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data["name"], team_abbr, players)

            if not player:
                continue

            punting.append(
                PlayerPunts(
                    player=player,
                    punts=stats["PUNTING_NO"]["statValue"],
                    punt_yards=stats["PUNTING_YDS"]["statValue"],
                    punt_long=stats["PUNTING_LNG"]["statValue"],
                )
            )

        return punting

    def map_punt_returns(self, punt_return_data: dict, team_abbr: str, players: dict[str, Player]) -> PlayerPuntReturns:
        punt_returns: list[PlayerPuntReturns] = []

        for player_data in punt_return_data:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data["name"], team_abbr, players)

            if not player:
                continue

            punt_returns.append(
                PlayerPuntReturns(
                    player=player,
                    punt_returns=stats["PUNTRETURN_NO"]["statValue"],
                    punt_returns_yards=stats["PUNTRETURN_YDS"]["statValue"],
                    punt_returns_touchdowns=0,  # ack no touchdowns?!?!?
                    punt_returns_long=stats["PUNTRETURN_LNG"]["statValue"],
                )
            )

        return punt_returns

    def map_kick_returns(self, kick_return_data: dict, team_abbr: str, players: dict[str, Player]) -> PlayerKickReturns:
        kick_returns: list[PlayerKickReturns] = []

        for player_data in kick_return_data:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data["name"], team_abbr, players)

            if not player:
                continue

            kick_returns.append(
                PlayerKickReturns(
                    player=player,
                    kick_returns=stats["KICKRETURN_NO"]["statValue"],
                    kick_returns_yards=stats["KICKRETURN_YDS"]["statValue"],
                    kick_returns_touchdowns=0,  # ack, no touchdowns?!?!?
                    kick_returns_long=stats["KICKRETURN_LNG"]["statValue"],
                )
            )

        return kick_returns

    def map_field_goals(self, kicking_data: dict, team_abbr: str, players: dict[str, Player]) -> PlayerFieldGoals:
        field_goals: list[PlayerFieldGoals] = []

        for player_data in kicking_data if kicking_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}

            if not stats.get("FIELDGOALS_FGFGA"):  # cfl mixes field goals and singles into this data
                continue

            player = self._get_player(player_data["name"], team_abbr, players)

            if not player:
                continue

            success_attempts = stats["FIELDGOALS_FGFGA"]["statValue"].split("/")

            if len(success_attempts) != 2:
                StriveLogger.warn(f"Failed to parse field goal attempts for {player.first_name} {player.last_name}")
                continue

            field_goals.append(
                PlayerFieldGoals(
                    player=player,
                    field_goal_attempts=success_attempts[1],
                    field_goal_made=success_attempts[0],
                    # have blocked here
                )
            )

        return field_goals

    def map_one_point_converts(self, one_point_convert_data: dict, team_abbr: str, players: dict[str, Player]) -> PlayerOnePointConverts:
        one_point_converts: list[PlayerOnePointConverts] = []

        for player_data in one_point_convert_data if one_point_convert_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}

            if not stats.get("FIELDGOALS_XP"):  # cfl mixes field goals and singles into this data
                continue

            player = self._get_player(player_data["name"], team_abbr, players)

            if not player:
                continue

            one_point_converts.append(
                PlayerOnePointConverts(
                    player=player,
                    one_point_converts_attempts=0,  # attempts missing
                    one_point_converts_made=stats["FIELDGOALS_XP"]["statValue"],
                )
            )

        return one_point_converts

    def map_defence(self, defence_data: dict, team_abbr: str, players: dict[str, Player]) -> PlayerDefence:
        defence: list[PlayerDefence] = []

        for player_data in defence_data if defence_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data["name"], team_abbr, players)

            if not player:
                continue

            defence.append(
                PlayerDefence(
                    player=player,
                    fumbles_forced=stats.get("DEFENCE_FF")["statValue"] if stats.get("DEFENCE_FF") else 0,
                    interceptions=stats.get("DEFENCE_INT")["statValue"] if stats.get("DEFENCE_INT") else 0,
                    passes_knocked_down=0,  # missing :(
                    sacks_qb_made=stats.get("DEFENCE_SK")["statValue"] if stats.get("DEFENCE_SK") else 0,
                    tackles_defensive=stats.get("DEFENCE_SOLO")["statValue"] if stats.get("DEFENCE_TKL") else 0,
                    # have tackles for loss here
                )
            )

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
