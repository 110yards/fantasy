# generated by datamodel-codegen:
#   filename:  game.json
#   timestamp: 2021-03-19T11:38:10+00:00

from __future__ import annotations
from api.app.core.sim_state import SimState

from api.app.domain.entities.game_player import GamePlayer
from api.app.domain.entities.player_game import PlayerGame
from api.app.domain.enums.position_type import PositionType

from typing import Dict, List, Optional

from api.app.core.base_entity import BaseEntity
from api.app.core.hash_dict import hash_dict
from api.app.domain.entities.event_status import EventStatus
from api.app.domain.entities.event_type import EventType
from api.app.domain.entities.game_score import GameScore
from api.app.domain.entities.game_teams import GameTeams


class Game(BaseEntity):
    date_start: str
    game_number: int
    week: int
    season: int
    game_duration: Optional[int]
    event_type: EventType
    event_status: EventStatus
    score: GameScore
    teams: GameTeams
    player_stats: Dict[str, PlayerGame]
    hash: Optional[str]
    away_roster: Optional[Dict[str, GamePlayer]]
    home_roster: Optional[Dict[str, GamePlayer]]

    def calculate_hash(self):
        for stats in self.player_stats.values():
            stats.calculate_hash()

        self.hash = hash_dict(self.dict(exclude={"away_roster": ..., "home_roster": ...}))


def from_cfl(game: dict, count_away_players: bool, count_home_players: bool, sim_state: Optional[SimState]) -> Game:
    game["id"] = str(game["game_id"])

    # this code is used for simulating game progress during the offseason
    if sim_state:
        sim_state.apply_to_score(game)
    # end of simulation code

    game["score"] = {
        "away": game["team_1"]["score"],
        "home": game["team_2"]["score"],
    }

    game["teams"] = {
        "away": clean_team(game["team_1"]),
        "home": clean_team(game["team_2"]),
    }

    if count_away_players:
        stats1 = get_team_player_stats(
            game["id"],
            game["week"],
            game["boxscore"]["teams"]["team_1"],
            game["rosters"]["teams"]["team_1"]["roster"],
            game["teams"]["away"],
            game["teams"]["home"],
        )
    else:
        stats1 = []

    if count_home_players:
        stats2 = get_team_player_stats(
            game["id"],
            game["week"],
            game["boxscore"]["teams"]["team_2"],
            game["rosters"]["teams"]["team_2"]["roster"],
            game["teams"]["home"],
            game["teams"]["away"],
        )
    else:
        stats2 = []

    all_stats = stats1 + stats2
    game["player_stats"] = {stats["player_id"]: stats for stats in all_stats}

    # More simulation code
    if sim_state:
        sim_state.apply_to_stats(game)

    game_entity = Game.parse_obj(game)
    game_entity.away_roster = get_roster(game["rosters"]["teams"]["team_1"]["roster"])
    game_entity.home_roster = get_roster(game["rosters"]["teams"]["team_2"]["roster"])

    game_entity.calculate_hash()

    return game_entity


def get_roster(roster: List[Dict]) -> Dict[str, GamePlayer]:
    game_roster = {}
    for player in roster:
        player["position"] = PositionType.from_cfl_roster(player["position"])
        player["id"] = str(player["cfl_central_id"])
        game_player = GamePlayer.parse_obj(player)

        game_roster[game_player.id] = game_player

    return game_roster


def clean_team(team: dict):
    return {
        "id": team["team_id"],
        "location": team["location"],
        "name": team["nickname"],
        "abbreviation": team["abbreviation"],
    }


def get_team_player_stats(game_id: str, week: int, boxscore: dict, roster: dict, team: dict, opponent: dict):
    team_stats = []

    for player in roster:
        if player["position"] == "OL" or player["position"] == "OT":
            continue

        player_stats = get_player_stats(game_id, week, boxscore["players"], player, team, opponent)
        player_stats["game_id"] = game_id
        team_stats.append(player_stats)

    return team_stats


def get_player_stats(game_id: int, week: int, boxscore: dict, player: dict, team: dict, opponent: dict):
    defence = get_player_stats_for_category(boxscore["defence"], player["cfl_central_id"])
    field_goals = get_player_stats_for_category(boxscore["field_goals"], player["cfl_central_id"])
    kick_returns = get_player_stats_for_category(boxscore["kick_returns"], player["cfl_central_id"])
    kicking = get_player_stats_for_category(boxscore["kicking"], player["cfl_central_id"])
    one_point_converts = get_player_stats_for_category(boxscore["one_point_converts"], player["cfl_central_id"])
    passing = get_player_stats_for_category(boxscore["passing"], player["cfl_central_id"])
    punt_returns = get_player_stats_for_category(boxscore["punt_returns"], player["cfl_central_id"])
    punts = get_player_stats_for_category(boxscore["punts"], player["cfl_central_id"])
    receiving = get_player_stats_for_category(boxscore["receiving"], player["cfl_central_id"])
    rushing = get_player_stats_for_category(boxscore["rushing"], player["cfl_central_id"])
    two_point_converts = get_player_stats_for_category(boxscore["two_point_converts"], player["cfl_central_id"])
    field_goal_returns = get_player_stats_for_category(boxscore["field_goal_returns"], player["cfl_central_id"])

    stats = {}
    stats.update(defence)
    stats.update(field_goals)
    stats.update(kick_returns)
    stats.update(kicking)
    stats.update(one_point_converts)
    stats.update(passing)
    stats.update(punt_returns)
    stats.update(punts)
    stats.update(receiving)
    stats.update(rushing)
    stats.update(two_point_converts)
    stats.update(field_goal_returns)

    if "field_goal_made" in stats:
        stats["field_goal_misses"] = stats["field_goal_attempts"] - stats["field_goal_made"]

    player["id"] = str(player["cfl_central_id"])
    player["position"] = PositionType.from_cfl_roster(player["position"])

    combined = {
        "id": PlayerGame.create_id(player["id"], game_id),
        "game_id": game_id,
        "week_number": week,
        "stats": stats,
        "player_id": player["id"],
        "team": team,
        "opponent": opponent,
    }

    return combined


def get_player_stats_for_category(stats: dict, player_id: int):
    if not stats:
        return []

    for item in stats:
        if item["player"]["cfl_central_id"] == player_id:
            return item

    return []
