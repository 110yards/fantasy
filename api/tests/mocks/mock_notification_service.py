from fastapi.param_functions import Depends
from api.app.domain.entities.league import League
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from api.app.domain.services.discord_service import DiscordService, create_discord_service


def create_notification_service(
    config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    discord_service: DiscordService = Depends(create_discord_service),
):
    return NotificationService(
        config_repo=config_repo,
        discord_service=discord_service,
    )


class MockNotificationService:

    def send_draft_event(self, league: League, message: str):
        pass

    def send_transaction_event(self, league: League, message: str):
        pass

    def send_waiver_results(self, league: League, message: str):
        pass

    def send_weekly_summary(self, league: League, message: str):
        pass
