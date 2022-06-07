from yards_py.core.firestore_proxy import Query
from typing import List
from yards_py.domain.entities.league import League
from services.api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from fastapi import Depends


def create_league_problems_service(league_repo: LeagueRepository = Depends(create_league_repository)):
    return LeagueProblemsService(league_repo)


class LeagueProblemsService:
    def __init__(self, league_repo: LeagueRepository):
        self.league_repo = league_repo

    def get_leagues_with_problems(self) -> List[League]:
        missing_commands_sub = self.league_repo.where(Query("league_command_subscription", "==", False))

        leagues = {league.id: league for league in missing_commands_sub}

        # for league in missing_stats_sub:
        #     if league.id not in leagues:
        #         leagues[league.id] = league

        return list(leagues.values())
