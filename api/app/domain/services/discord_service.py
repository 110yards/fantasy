from fastapi.param_functions import Depends
import requests

from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository


def create_discord_service(public_repo: PublicRepository = Depends(create_public_repository)):
    enabled = public_repo.get_switches().enable_discord_integration
    return DiscordService(enabled)


class DiscordService:
    def __init__(self, enabled: bool):
        self.enabled = enabled

    def send_message(self, url: str, message: str):
        if self.enabled:
            requests.post(url, json={
                "content": message
            })

    def send_test_notification(self, url):
        self.send_message(url, "It works!")
