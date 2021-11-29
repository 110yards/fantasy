import requests


def create_discord_service():
    return DiscordService()


class DiscordService:

    def send_message(self, url: str, message: str):
        requests.post(url, json={
            "content": message
        })

    def send_test_notification(self, url):
        self.send_message(url, "It works!")
