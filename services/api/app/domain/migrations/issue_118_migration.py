
from typing import Dict, List

from fastapi.param_functions import Depends
from services.api.app.cfl.cfl_game_proxy import (CflGameProxy,
                                                 create_cfl_game_proxy)
from services.api.app.domain.enums.draft_state import DraftState
from services.api.app.domain.repositories.league_repository import (
    LeagueRepository, create_league_repository)
from services.api.app.domain.repositories.league_week_matchup_repository import (
    LeagueWeekMatchupRepository, create_league_week_matchup_repository)
from services.api.app.domain.repositories.player_league_season_score_repository import (
    PlayerLeagueSeasonScoreRepository,
    create_player_league_season_score_repository)
from yards_py.domain.entities.roster import Roster


def create_issue_118_migration(
    league_repo=Depends(create_league_repository),
    matchup_repo: LeagueWeekMatchupRepository = Depends(create_league_week_matchup_repository),
    player_score_repo: PlayerLeagueSeasonScoreRepository = Depends(create_player_league_season_score_repository),
    cfl_game_proxy: CflGameProxy = Depends(create_cfl_game_proxy),
):
    return Issue118Migration(league_repo, matchup_repo, player_score_repo, cfl_game_proxy)


class Issue118Migration:
    '''Fixes large schedule configs https://github.com/mdryden/110yards-api/issues/102'''

    def __init__(
        self,
        league_repo: LeagueRepository,
        matchup_repo: LeagueWeekMatchupRepository,
        player_score_repo: PlayerLeagueSeasonScoreRepository,
        cfl_game_proxy: CflGameProxy,
    ):
        self.league_repo = league_repo
        self.matchup_repo = matchup_repo
        self.player_score_repo = player_score_repo
        self.cfl_game_proxy = cfl_game_proxy

    def run(self, league_id, start: int, end: int) -> str:

        if league_id:
            leagues = [self.league_repo.get(league_id)]
        else:
            leagues = self.league_repo.get_all()

        # get all games for included weeks from cfl
        games_by_week: Dict[int, List[str]] = {}

        for week_number in range(start, end + 1):
            games_for_week = self.cfl_game_proxy.get_game_summaries_for_week(2021, week_number)
            game_ids = [str(g["game_id"]) for g in games_for_week["data"]]
            games_by_week[week_number] = game_ids

        league_count = 0

        for league in leagues:
            if league.draft_state != DraftState.COMPLETE:
                continue

            for week_number in range(start, end + 1):
                matchups = self.matchup_repo.get_all(league.id, week_number)

                for matchup in matchups:
                    if matchup.away:
                        self.fix_roster(week_number, league_id, matchup.away, games_by_week)

                    if matchup.home:
                        self.fix_roster(week_number, league_id, matchup.home, games_by_week)

                    self.matchup_repo.set(league.id, week_number, matchup)

            league_count += 1

        result = f"Recalculated matchup scores for {league_count} leagues."

        return result

    def fix_roster(self, week_number: int, league_id, roster: Roster, games_by_week: Dict[int, List[str]]):
        for position in roster.positions.values():
            if not position.is_starting_position_type() or not position.player:
                continue

            player_score = self.player_score_repo.get(league_id, position.player.id)
            if not player_score:
                continue

            for game_id in games_by_week[week_number]:
                if game_id in player_score.game_scores:
                    game_score = player_score.game_scores[game_id]
                    position.game_score = game_score.total_score

        roster.this_week_points_for = roster.calculate_score()
