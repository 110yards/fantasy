# import uuid
# from datetime import datetime, timedelta, timezone

# import requests
# from dateutil import parser
# from fastapi import Depends
# from strivelogger import StriveLogger

# from app.config.settings import Settings, get_settings
# from app.domain.models.game import (
#     Boxscore,
#     BoxscoreTeam,
#     BoxscoreTeams,
#     EventStatus,
#     Game,
#     GamePlayer,
#     GamePlayers,
#     PlayerDefence,
#     PlayerFieldGoals,
#     PlayerKickReturns,
#     PlayerOnePointConverts,
#     PlayerPassing,
#     PlayerPuntReturns,
#     PlayerPunts,
#     PlayerReceiving,
#     PlayerRushing,
#     RosterPlayer,
#     Rosters,
#     RosterTeam,
#     RosterTeams,
#     Team,
# )
# from app.domain.models.player import Player
# from app.domain.store.player_store import PlayerStore, create_player_store
# from app.domain.store.schedule_store import ScheduleStore, create_schedule_store

# # TSN Notes
# # stats page (player list) has fumble data


# class ActiveGamesService:
#     def __init__(
#         self,
#         settings: Settings,
#         player_store: PlayerStore,
#         schedule_store: ScheduleStore,
#     ):
#         self.settings = settings
#         self.player_store = player_store
#         self.schedule_store = schedule_store
#         self.players: dict[int, Player] = {}

#     def get_games(self, hours: int) -> list[Game]:
#         year = datetime.now().year
#         schedule = self.schedule_store.get_schedule(year)

#         if not schedule:
#             StriveLogger.error("No schedule found in store")
#             return []

#         players = self.player_store.get_players(year)

#         if not players:
#             StriveLogger.error("No players found in store")
#             return []

#         self.rostered_players: dict[str, Player] = {}

#         hours = hours or 24
#         scope_start = datetime.now(timezone.utc) - timedelta(hours=hours)
#         scope_end = datetime.now(timezone.utc) + timedelta(hours=hours)

#         in_scope = [game for game in schedule.games.values() if scope_start <= parser.isoparse(game.date_start) <= scope_end]

#         games = [self.update_from_tsn(game) for game in in_scope]

#         return [game for game in games if game is not None]

#     def update_from_tsn(self, schedule_game: Game) -> Game:
#         url = f"https://stats.sports.bellmedia.ca/sports/football/leagues/cfl/eventV2/{schedule_game.tsn_game_id}?type=json"
#         # url = f"https://stats.sports.bellmedia.ca/sports/football/leagues/cfl/event/{schedule_game.tsn_game_id}/eventPlayerStatsByCompetitor?type=json"

#         response = requests.get(url)
#         StriveLogger.info(f"TSN API call: {url}")

#         if response.headers.get("Content-Type") != "application/json":
#             return schedule_game

#         data = response.json()
#         game = self.map_tsn_game(schedule_game, data)

#         return game

#     def map_tsn_game(self, schedule_game: Game, game_data: dict) -> Game:
#         game = schedule_game.copy(deep=True)

#         game.event_status = self.map_tsn_status(game_data["event"]["status"])

#         game.team_1 = self.map_tsn_team(game.team_1, game_data["event"]["top"], False)
#         game.team_2 = self.map_tsn_team(game.team_2, game_data["event"]["bottom"], True)
#         # confirmed with 2017 tie that neither is marked as winner
#         game.team_1.is_winner = game.team_1.score > game.team_2.score
#         game.team_2.is_winner = game.team_2.score > game.team_1.score

#         game.boxscore = self.map_tsn_boxscore(schedule_game)
#         game.rosters = Rosters(
#             teams=RosterTeams(
#                 team_1=RosterTeam(
#                     team_id=schedule_game.team_1.team_id,
#                     abbreviation=schedule_game.team_1.abbreviation,
#                     roster=[self.to_roster_player(p) for p in self.rostered_players.values() if p.team.team_id == schedule_game.team_1.team_id],
#                 ),
#                 team_2=RosterTeam(
#                     team_id=schedule_game.team_2.team_id,
#                     abbreviation=schedule_game.team_2.abbreviation,
#                     roster=[self.to_roster_player(p) for p in self.rostered_players.values() if p.team.team_id == schedule_game.team_2.team_id],
#                 ),
#             )
#         )

#         return game

#     def to_roster_player(self, player: Player) -> RosterPlayer:
#         return RosterPlayer(
#             player_id=player.player_id,
#             first_name=player.first_name,
#             last_name=player.last_name,
#             position=player.position.abbreviation,
#             birth_date=player.birth_date,
#         )

#     def map_tsn_status(self, text: str) -> EventStatus:
#         match text.lower():
#             case "pre-game":
#                 return EventStatus.pre_game()
#             case "final":
#                 return EventStatus.final()
#             case _:
#                 StriveLogger.warn(f"Unknown status: {text}")
#                 return EventStatus.pre_game()

#     def map_tsn_team(self, schedule_team: Team, team_data: dict, is_home: bool) -> Team:
#         team = schedule_team.copy(deep=True)
#         team.score = team_data["score"] or 0
#         team.is_at_home = is_home
#         return team

#     def map_tsn_boxscore(self, schedule_game: Game) -> Boxscore:
#         url = f"https://stats.sports.bellmedia.ca/sports/football/leagues/cfl/event/{schedule_game.tsn_game_id}/eventPlayerStatsByCompetitor?type=json"

#         response = requests.get(url)
#         StriveLogger.info(f"TSN API stats call: {url}")

#         if response.headers.get("Content-Type") != "application/json":
#             return None

#         player_data = response.json()

#         team_1 = BoxscoreTeam(
#             team_id=schedule_game.team_1.team_id,
#             abbreviation=schedule_game.team_1.abbreviation,
#             players=self.map_boxscore_players(player_data["away"]["playerStatsByCategory"]),
#         )

#         team_2 = BoxscoreTeam(
#             team_id=schedule_game.team_2.team_id,
#             abbreviation=schedule_game.team_2.abbreviation,
#             players=self.map_boxscore_players(player_data["home"]["playerStatsByCategory"]),
#         )

#         boxscore = Boxscore(
#             teams=BoxscoreTeams(
#                 team_1=team_1,
#                 team_2=team_2,
#             )
#         )

#         return boxscore

#     def map_boxscore_players(self, team_player_data: dict) -> GamePlayers:
#         return GamePlayers(
#             passing=self.map_passing(team_player_data["passing"]),
#             rushing=self.map_rushing(team_player_data["rushing"]),
#             receiving=self.map_receiving(team_player_data["receiving"]),
#             punts=self.map_punts(team_player_data["punting"]),
#             punt_returns=self.map_punt_returns(team_player_data["puntReturning"]),
#             kick_returns=self.map_kick_returns(team_player_data["kickReturning"]),
#             field_goals=self.map_field_goals(team_player_data["kicking"]),
#             # field_goal_returns=
#             # kicking=self.map_kicking(team_player_data["kicking"]),
#             one_point_converts=self.map_one_point_converts(team_player_data["kicking"]),
#             defence=self.map_defence(team_player_data["defense"]),
#         )

#     def create_game_player(self, player: Player) -> GamePlayer:
#         self.rostered_players[player.player_id] = player

#         return GamePlayer(
#             player_id=player.player_id,
#             tsn_id=player.tsn_id,
#             first_name=player.first_name,
#             last_name=player.last_name,
#             birth_date=player.birth_date,
#         )

#     def get_player(self, player_data: int) -> GamePlayer:
#         tsn_id = player_data["playerId"]
#         player = self.players.get(tsn_id)

#         if player:
#             return self.create_game_player(player)

#         player = Player(
#             player_id=uuid.uuid4().hex,
#             tsn_id=tsn_id,
#             first_name=player_data["firstName"],
#             last_name=player_data["lastName"],
#             foreign_player=player_data.get("country") != "Canada",
#             position=tsn.map_tsn_position(player_data["positionShort"]),
#             team=tsn.map_tsn_teams(player_data["competitorId"], player_data["number"]),
#         )

#         self.player_store.save_player(datetime.now().year, player)
#         self.players[tsn_id] = player

#         return self.create_game_player(player)

#     def map_passing(self, passing_data: dict) -> PlayerPassing:
#         passing: list[PlayerPassing] = []

#         for player_data in passing_data if passing_data else []:
#             passing.append(
#                 PlayerPassing(
#                     player=self.get_player(player_data["player"]),
#                     pass_attempts=player_data["stats"]["passingAttempts"],
#                     pass_completions=player_data["stats"]["passingCompleted"],
#                     pass_net_yards=player_data["stats"]["passingYards"],
#                     pass_touchdowns=player_data["stats"]["passingTouchdowns"],
#                     pass_interceptions=player_data["stats"]["passingInterceptions"],
#                 )
#             )

#         return passing

#     def map_rushing(self, rushing_data: dict) -> PlayerRushing:
#         rushing: list[PlayerRushing] = []

#         for player_data in rushing_data if rushing_data else []:
#             rushing.append(
#                 PlayerRushing(
#                     player=self.get_player(player_data["player"]),
#                     rush_attempts=player_data["stats"]["rushingAttempts"],
#                     rush_net_yards=player_data["stats"]["rushingYards"],
#                     rush_touchdowns=player_data["stats"]["rushingTouchdowns"],
#                 )
#             )

#         return rushing

#     def map_receiving(self, receiving_data: dict) -> PlayerReceiving:
#         receiving: list[PlayerReceiving] = []

#         for player_data in receiving_data if receiving_data else []:
#             receiving.append(
#                 PlayerReceiving(
#                     player=self.get_player(player_data["player"]),
#                     receive_caught=player_data["stats"]["receivingReceptions"],
#                     receive_yards=player_data["stats"]["receivingYards"],
#                     receive_touchdowns=player_data["stats"]["receivingTouchdowns"],
#                     receive_long=player_data["stats"]["receivingLong"],
#                 )
#             )

#         return receiving

#     def map_punts(self, punting_data: dict) -> PlayerPunts:
#         punting: list[PlayerPunts] = []

#         for player_data in punting_data if punting_data else []:
#             punting.append(
#                 PlayerPunts(
#                     player=self.get_player(player_data["player"]),
#                     punts=player_data["stats"]["puntingPunts"],
#                     punt_yards=player_data["stats"]["puntingYards"],
#                     punt_long=player_data["stats"]["puntingLong"],
#                 )
#             )

#         return punting

#     def map_punt_returns(self, punt_return_data: dict) -> PlayerPuntReturns:
#         punt_returns: list[PlayerPuntReturns] = []

#         for player_data in punt_return_data:
#             punt_returns.append(
#                 PlayerPuntReturns(
#                     player=self.get_player(player_data["player"]),
#                     punt_returns=player_data["stats"]["puntReturningReturns"],
#                     punt_returns_yards=player_data["stats"]["puntReturningYards"],
#                     punt_returns_touchdowns=player_data["stats"]["puntReturningTouchdowns"],
#                     punt_returns_long=player_data["stats"]["puntReturningLong"],
#                 )
#             )

#         return punt_returns

#     def map_kick_returns(self, kick_return_data: dict) -> PlayerKickReturns:
#         kick_returns: list[PlayerKickReturns] = []

#         for player_data in kick_return_data:
#             kick_returns.append(
#                 PlayerKickReturns(
#                     player=self.get_player(player_data["player"]),
#                     kick_returns=player_data["stats"]["kickReturningReturns"],
#                     kick_returns_yards=player_data["stats"]["kickReturningYards"],
#                     kick_returns_touchdowns=player_data["stats"]["kickReturningTouchdowns"],
#                     kick_returns_long=player_data["stats"]["kickReturningLong"],
#                 )
#             )

#         return kick_returns

#     def map_field_goals(self, kicking_data: dict) -> PlayerFieldGoals:
#         field_goals: list[PlayerFieldGoals] = []

#         for player_data in kicking_data if kicking_data else []:
#             field_goals.append(
#                 PlayerFieldGoals(
#                     player=self.get_player(player_data["player"]),
#                     field_goal_attempts=player_data["stats"]["kickingFieldGoalsAttempted"],
#                     field_goal_made=player_data["stats"]["kickingFieldGoalsMade"],
#                     # have blocked here
#                 )
#             )

#         return field_goals

#     # def map_field_goals_returns(self, field_goal_return_data: dict) -> PlayerFieldGoalReturns:
#     #     field_goal_returns: list[PlayerFieldGoalReturns] = []

#     #     for player_data in field_goal_return_data:
#     #         field_goal_returns.append(
#     #             PlayerFieldGoalReturns(
#     #                 player=self.get_player(player_data["player"]),
#     #                 field_goal_returns=player_data["stats"]["fieldGoalReturningReturns"],
#     #                 field_goal_returns_yards=player_data["stats"]["fieldGoalReturningYards"],
#     #                 field_goal_returns_touchdowns=player_data["stats"]["fieldGoalReturningTouchdowns"],
#     #                 field_goal_returns_long=player_data["stats"]["fieldGoalReturningLong"],
#     #             )
#     #         )

#     #     return field_goal_returns

#     # def map_kicking(self, kicking_data: dict) -> PlayerKicking:
#     #     kicking: list[PlayerKicking] = []

#     #     for player_data in kicking_data:
#     #         kicking.append(
#     #             PlayerKicking(
#     #                 player=self.get_player(player_data["player"]),
#     #                 kickoffs=player_data["stats"]["kickingKickoffs"],
#     #                 kickoff_yards=player_data["stats"]["kickingKickoffYards"],
#     #                 kickoff_long=player_data["stats"]["kickingKickoffLong"],
#     #                 kickoff_touchbacks=player_data["stats"]["kickingKickoffTouchbacks"],
#     #             )
#     #         )

#     #     return kicking

#     def map_one_point_converts(self, one_point_convert_data: dict) -> PlayerOnePointConverts:
#         one_point_converts: list[PlayerOnePointConverts] = []

#         for player_data in one_point_convert_data if one_point_convert_data else []:
#             one_point_converts.append(
#                 PlayerOnePointConverts(
#                     player=self.get_player(player_data["player"]),
#                     one_point_converts_attempts=player_data["stats"]["kickingExtraPointsAttempted"],
#                     one_point_converts_made=player_data["stats"]["kickingExtraPointsMade"],
#                 )
#             )

#         return one_point_converts

#     def map_defence(self, defence_data: dict) -> PlayerDefence:
#         defence: list[PlayerDefence] = []

#         for player_data in defence_data if defence_data else []:
#             defence.append(
#                 PlayerDefence(
#                     player=self.get_player(player_data["player"]),
#                     fumbles_forced=player_data["stats"]["defenceForcedFumbles"],
#                     interceptions=player_data["stats"]["defenseInterceptions"],
#                     passes_knocked_down=player_data["stats"]["defensePassesDefensed"],
#                     sacks_qb_made=player_data["stats"]["defenseSacks"],
#                     tackles_defensive=player_data["stats"]["defenseTackles"],
#                     # have assisted tackles here
#                 )
#             )

#         return defence


# def create_active_games_service(
#     settings: Settings = Depends(get_settings),
#     player_store: PlayerStore = Depends(create_player_store),
#     schedule_store: ScheduleStore = Depends(create_schedule_store),
# ) -> ActiveGamesService:
#     return ActiveGamesService(
#         settings=settings,
#         player_store=player_store,
#         schedule_store=schedule_store,
#     )
