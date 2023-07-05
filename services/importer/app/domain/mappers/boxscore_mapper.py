from abc import ABC, abstractmethod

from strivelogger import StriveLogger

from ..models.boxscore import PlayerStats, StatsCollection
from ..models.player import Player


class PlayerStatsMapper(ABC):
    def fill_player_stats(self, player_stats: StatsCollection, player_data: dict, available_players: list[Player]):
        self.map_passing(player_stats, player_data["passing"])
        self.map_rushing(player_stats, player_data["rushing"])
        self.map_receiving(player_stats, player_data["receiving"])
        self.map_punts(player_stats, player_data["punts"])
        self.map_punt_returns(player_stats, player_data["puntReturns"])
        self.map_kick_returns(player_stats, player_data["kickoffReturns"])
        self.map_field_goals(player_stats, player_data["fieldGoals"])
        self.map_one_point_converts(player_stats, player_data["fieldGoals"])
        self.map_defence(player_stats, player_data["defence"])
        # # field_goal_returns=
        # # kicking=map_kicking(team_player_data["kicking"]),

    @abstractmethod
    def _get_player(
        self,
        player_data: dict,
        stats: StatsCollection,
    ) -> PlayerStats:
        raise NotImplementedError()

    def map_passing(self, stats: StatsCollection, passing_data: dict):
        player = stats.get()

        for player_data in passing_data if passing_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data, stats)

            if not player:
                continue

            completion_attempts = stats["COMPLETIONS_ATTEMPTS"]["statValue"].split("/")

            if len(completion_attempts) != 2:
                StriveLogger.warn(f"Failed to parse completion attempts for {player.first_name} {player.last_name}")
                continue

            player.pass_attempts = completion_attempts[1]
            player.pass_completions = completion_attempts[0]
            player.pass_net_yards = stats["YARDS"]["statValue"]
            player.pass_touchdowns = stats["TOUCHDOWNS"]["statValue"]
            player.pass_interceptions = stats["INTERCEPTIONS"]["statValue"]

    def map_rushing(self, stats: StatsCollection, rushing_data: dict):
        for player_data in rushing_data if rushing_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data, stats)

            if not player:
                continue

            player.rush_attempts = (stats["CARRIES"]["statValue"],)
            player.rush_net_yards = (stats["YARDS"]["statValue"],)
            player.rush_touchdowns = (stats["TOUCHDOWNS"]["statValue"],)

    def map_receiving(self, stats: StatsCollection, receiving_data: dict):
        for player_data in receiving_data if receiving_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data, stats)

            if not player:
                continue

            player.receive_caught = (stats["RECEPTIONS"]["statValue"],)
            player.receive_yards = (stats["YARDS"]["statValue"],)
            player.receive_touchdowns = (stats["TOUCHDOWNS"]["statValue"],)
            player.receive_long = (0,)  # missing

    def map_punts(self, stats: StatsCollection, punting_data: dict):
        punting: list[PlayerPunts] = []

        for player_data in punting_data if punting_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data, stats)

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

    def map_punt_returns(self, stats: StatsCollection, punt_return_data: dict):
        punt_returns: list[PlayerPuntReturns] = []

        for player_data in punt_return_data:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data, stats)

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

    def map_kick_returns(self, stats: StatsCollection, kick_return_data: dict):
        kick_returns: list[PlayerKickReturns] = []

        for player_data in kick_return_data:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data, stats)

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

    def map_field_goals(self, stats: StatsCollection, kicking_data: dict):
        field_goals: list[PlayerFieldGoals] = []

        for player_data in kicking_data if kicking_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}

            if not stats.get("FIELDGOALS_FGFGA"):  # source mixes field goals and singles into this data
                continue

            player = self._get_player(player_data, stats)

            if not player:
                continue

            success_attempts = stats["FIELDGOALS_FGFGA"]["statValue"].split("/")

            if len(success_attempts) != 2:
                StriveLogger.warn(f"Failed to parse field goal attempts for {player.first_name} {player.last_name}")
                continue

            field_goals.append(
                PlayerFieldGoals(
                    player=player,
                    field_goal_attempts=int(success_attempts[1]),
                    field_goal_made=int(success_attempts[0]),
                    # have blocked here
                )
            )

        return field_goals

    def map_one_point_converts(self, stats: StatsCollection, one_point_convert_data: dict) -> PlayerOnePointConverts:
        one_point_converts: list[PlayerOnePointConverts] = []

        for player_data in one_point_convert_data if one_point_convert_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}

            if not stats.get("FIELDGOALS_XP"):  # source mixes field goals and singles into this data
                continue

            player = self._get_player(player_data, stats)

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

    def map_defence(self, stats: StatsCollection, defence_data: dict):
        defence: list[PlayerDefence] = []

        for player_data in defence_data if defence_data else []:
            stats = {s["name"]: s for s in player_data["stats"]}
            player = self._get_player(player_data, stats)

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
