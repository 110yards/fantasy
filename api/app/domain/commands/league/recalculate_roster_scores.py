
# from api.app.domain.enums.draft_state import DraftState
# from api.app.domain.repositories.league_repository import LeagueRepository
# from api.app.domain.entities.league_player_score import LeaguePlayerScore
# from api.app.domain.entities.game_player_stats import GamePlayerStats
# from api.app.domain.repositories.league_player_score_repository import LeaguePlayerScoreRepository, create_league_player_score_repository
# from typing import Optional
# from api.app.domain.repositories.state_repository import StateRepository, create_state_repository
# from api.app.domain.repositories.user_league_repository import UserLeagueRepository, create_user_league_repository
# from api.app.domain.repositories.league_week_matchup_repository import LeagueWeekMatchupRepository, create_league_week_matchup_repository
# from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
# from api.app.domain.repositories.league_owned_player_repository import LeagueOwnedPlayerRepository, create_league_owned_player_repository
# from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
# from api.app.core.annotate_args import annotate_args
# from api.app.core.base_command_executor import (BaseCommand, BaseCommandExecutor,
#                                             BaseCommandResult)
# from fastapi.param_functions import Depends
# from firebase_admin import firestore


# def create_recalculate_roster_scores_command_executor(
#     state_repo: StateRepository = Depends(create_state_repository),
#     league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
#     league_owned_players_repo: LeagueOwnedPlayerRepository = Depends(create_league_owned_player_repository),
#     league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
#     league_matchup_repo: LeagueWeekMatchupRepository = Depends(create_league_week_matchup_repository),
#     user_league_repo: UserLeagueRepository = Depends(create_user_league_repository),
#     league_player_score_repo: LeaguePlayerScoreRepository = Depends(create_league_player_score_repository),
# ):
#     return RecalculateRosterScoresCommandExecutor(
#         state_repo=state_repo,
#         league_config_repo=league_config_repo,
#         league_owned_players_repo=league_owned_players_repo,
#         league_roster_repo=league_roster_repo,
#         league_matchup_repo=league_matchup_repo,
#         user_league_repo=user_league_repo,
#         league_player_score_repo=league_player_score_repo)


# @annotate_args
# class RecalculateRosterScoresCommand(BaseCommand):
#     league_id: Optional[str]


# @annotate_args
# class RecalculateRosterScoresResult(BaseCommandResult[RecalculateRosterScoresCommand]):
#     pass


# class RecalculateRosterScoresCommandExecutor(BaseCommandExecutor[RecalculateRosterScoresCommand, RecalculateRosterScoresResult]):

#     def __init__(
#         self,
#         state_repo: StateRepository,
#         league_config_repo: LeagueConfigRepository,
#         league_owned_players_repo: LeagueOwnedPlayerRepository,
#         league_roster_repo: LeagueRosterRepository,
#         league_matchup_repo: LeagueWeekMatchupRepository,
#         user_league_repo: UserLeagueRepository,
#         league_player_score_repo: LeaguePlayerScoreRepository,
#         league_repo: LeagueRepository,
#     ):
#         self.state_repo = state_repo
#         self.league_config_repo = league_config_repo
#         self.league_owned_players_repo = league_owned_players_repo
#         self.league_roster_repo = league_roster_repo
#         self.league_matchup_repo = league_matchup_repo
#         self.user_league_repo = user_league_repo
#         self.league_player_score_repo = league_player_score_repo
#         self.league_repo = league_repo

#     def on_execute(self, command: RecalculateRosterScoresCommand) -> RecalculateRosterScoresResult:

#         # Note - this does not recalc player scores, it assumes the scores are already correct

#         week = self.state_repo.get().current_week

#         @firestore.transactional
#         def update_player(transaction):
#             league = self.league_repo.get(command.league_id)
#             if league.draft_state != DraftState.COMPLETE:
#                 return RecalculateRosterScoresResult(command=command)

#             rosters = self.league_roster_repo.get_all(command.league_id, transaction)

#             for roster in rosters:
#                 # TODO: share this with the update_player_stats command (unless it goes away competely)
#                 if roster.current_matchup:
#                     roster_score = roster.calculate_score()
#                     bench_score = roster.calculate_bench_score()

#                     roster.this_week_points_for = roster_score
#                     roster.this_week_bench_points_for = bench_score

#                     week_index = week - 1

#                     matchup = self.league_matchup_repo.get(command.league_id, week, roster.current_matchup, transaction)
#                     matchup_preview = self.user_league_repo.get(roster.id, command.league_id, transaction)
#                     schedule = self.league_config_repo.get_schedule_config(command.league_id, transaction)
#                     schedule_matchup = next(m for m in schedule.weeks[week_index].matchups if m.id == matchup.id)

#                     opponent_id: str = None

#                     if matchup.away and matchup.away.id == roster.id:
#                         opponent_id = matchup.home.id if matchup.home else None

#                         matchup.away_score = roster_score
#                         matchup.away_bench_score = bench_score

#                         matchup_preview.matchup.away_score = roster_score
#                         schedule_matchup.away_score = roster_score

#                     if matchup.home and matchup.home.id == roster.id:
#                         opponent_id = matchup.away.id if matchup.away else None

#                         matchup.home_score = roster_score
#                         matchup.home_bench_score = bench_score

#                         matchup_preview.matchup.home_score = roster_score
#                         schedule_matchup.home_score = roster_score

#                     if opponent_id:
#                         self.user_league_repo.set(opponent_id, matchup_preview, transaction)

#                     self.league_matchup_repo.set(command.league_id, week, matchup, transaction)
#                     self.user_league_repo.set(roster.id, matchup_preview, transaction)
#                     self.league_config_repo.set_schedule_config(command.league_id, schedule, transaction)

#                     self.league_roster_repo.set(command.league_id, roster, transaction)

#             # update the player scores list for the league (player id + stats, not updated when player details change)
#             self.league_player_score_repo.set(command.league_id, player_score, transaction)

#             return RecalculateRosterScoresResult(command=command)

#         transaction = self.league_roster_repo.firestore.create_transaction()
#         return update_player(transaction)
