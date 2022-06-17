

from fastapi import Depends
from yards_py.core.firestore_proxy import Query
from yards_py.domain.entities.roster import DEFAULT_WAIVER_BUDGET
from yards_py.domain.entities.waiver_bid import WaiverBidResult
from yards_py.domain.repositories.league_repository import LeagueRepository, create_league_repository
from yards_py.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from yards_py.domain.repositories.league_week_repository import LeagueWeekRepository, create_league_week_repository
from yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository


def create_recalc_waiver_budgets_service(
    public_repo: PublicRepository = Depends(create_public_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    league_week_repo: LeagueWeekRepository = Depends(create_league_week_repository),
):
    return RecalcWaiverBudgetsService(
        public_repo=public_repo,
        league_repo=league_repo,
        roster_repo=roster_repo,
        league_week_repo=league_week_repo,
    )


class RecalcWaiverBudgetsService:
    def __init__(
        self,
        public_repo: PublicRepository,
        league_repo: LeagueRepository,
        roster_repo: LeagueRosterRepository,
        league_week_repo: LeagueWeekRepository,
    ):
        self.public_repo = public_repo
        self.league_repo = league_repo
        self.roster_repo = roster_repo
        self.league_week_repo = league_week_repo

    def recalc(self) -> str:
        state = self.public_repo.get_state()
        current_season = state.current_season
        current_week = state.current_week

        query = Query("season", "==", current_season)
        leagues = self.league_repo.where(query)

        processed_leagues = []
        updated_rosters = []

        for league in leagues:
            if not league.is_active_for_season(current_season):
                continue

            processed_leagues.append(league)

            rosters = self.roster_repo.get_all(league.id)

            roster_budgets = {x.id: DEFAULT_WAIVER_BUDGET for x in rosters}
            has_bids = {x.id: False for x in rosters}

            for week in range(1, current_week):
                league_week = self.league_week_repo.get(league.id, week)
                if not league_week.waiver_bids:
                    continue  # no bids for week, nothing to count

                for bid in league_week.waiver_bids:
                    if bid.result == WaiverBidResult.Success:
                        has_bids[bid.roster_id] = True
                        roster_budgets[bid.roster_id] -= bid.amount

            for roster in rosters:
                if has_bids[roster.id] and roster.waiver_budget != roster_budgets[roster.id]:
                    self.roster_repo.partial_update(league.id, roster.id, {"waiver_budget": roster_budgets[roster.id]})
                    updated_rosters.append(roster)

        return f"Processed {len(processed_leagues)} leagues, updated {len(updated_rosters)} rosters."
