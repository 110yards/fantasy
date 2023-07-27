from datetime import datetime, timezone

from fastapi import Depends
from pydantic import BaseModel

from app.domain.repositories.league_owned_player_repository import LeagueOwnedPlayerRepository, create_league_owned_player_repository
from app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.domain.repositories.player_repository import PlayerRepository, create_player_repository


class OwnershipReportPlayer(BaseModel):
    player_name: str
    player_id: str
    ownership_count: int
    owned_percent: float

    def to_csv(self) -> str:
        return f"{self.player_name},{self.player_id},{self.ownership_count},{self.owned_percent}"


class OwnershipReport(BaseModel):
    generated_at: datetime
    league_count: int
    players: list[OwnershipReportPlayer]

    def to_csv(self) -> str:
        csv = f"Generated At:,{self.generated_at}\n"
        csv += f"League Count:,{self.league_count}\n\n"
        csv += "Player Name,Player ID,Ownership Count,Owned Percent\n"
        for player in self.players:
            csv += f"{player.to_csv()}\n"

        return csv


class OwnershipReportService:
    def __init__(
        self,
        league_repo: LeagueRepository,
        league_owned_player_repo: LeagueOwnedPlayerRepository,
        player_repo: PlayerRepository,
    ):
        self.league_repo = league_repo
        self.league_owned_player_repo = league_owned_player_repo
        self.player_repo = player_repo

    def get_ownership_report(self):
        season = datetime.now().year

        all_leagues = self.league_repo.get_all()
        active_leagues = [league for league in all_leagues if league.is_active_for_season(season)]

        league_count = len(active_leagues)

        owned_players: dict[str, int] = {}
        players = self.player_repo.get_all(season)
        for player in players:
            if player.player_id not in owned_players:
                owned_players[player.player_id] = 0

        for league in active_leagues:
            league_owned_players = self.league_owned_player_repo.get_all(league.id)

            for league_owned_player in league_owned_players:
                if league_owned_player.player_id in owned_players:  # deal with orphaned players
                    owned_players[league_owned_player.player_id] += 1

        players = {p.id: p for p in players}

        ownership_report_players = []
        for player_id, ownership_count in owned_players.items():
            player = players[player_id]
            owned_percent = ownership_count / league_count
            ownership_report_players.append(
                OwnershipReportPlayer(
                    player_name=player.full_name,
                    player_id=player.player_id,
                    ownership_count=ownership_count,
                    owned_percent=owned_percent,
                )
            )

        ownership_report_players.sort(key=lambda p: p.owned_percent, reverse=True)

        ownership_report = OwnershipReport(
            generated_at=datetime.now(tz=timezone.utc),
            league_count=league_count,
            players=ownership_report_players,
        )

        return ownership_report.to_csv()


def create_ownership_report_service(
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_owned_player_repo: LeagueOwnedPlayerRepository = Depends(create_league_owned_player_repository),
    player_repo: PlayerRepository = Depends(create_player_repository),
):
    return OwnershipReportService(
        league_repo=league_repo,
        league_owned_player_repo=league_owned_player_repo,
        player_repo=player_repo,
    )
