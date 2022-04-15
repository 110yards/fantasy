

from typing import List

from fastapi import Depends
from api.app.core.logging import Logger
from api.app.core.pubsub.pubsub_message import PubSubMessage
from api.app.core.pubsub.pubsub_push import PubSubPush
from api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from api.app.domain.repositories.virtual_pubsub_repository import VirtualPubSubPayload, VirtualPubsubRepository, create_virtual_pubsub_repository
from api.app.domain.services.end_of_week_service import EndOfWeekService, create_end_of_week_service
from api.app.domain.services.league_command_service import LeagueCommandService, create_league_command_service
from api.app.domain.services.waiver_service import WaiverService, create_waiver_service
from api.app.domain.topics import END_OF_WAIVERS_TOPIC, END_OF_WEEK_TOPIC, LEAGUE_COMMAND_TOPIC, LEAGUE_CREATED_TOPIC, UPDATE_PLAYERS_TOPIC


def create_dev_pubsub_service(
    repo: VirtualPubsubRepository = Depends(create_virtual_pubsub_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_command_service: LeagueCommandService = Depends(create_league_command_service),
    end_of_week_service: EndOfWeekService = Depends(create_end_of_week_service),
    waiver_service: WaiverService = Depends(create_waiver_service),
):
    return DevPubSubService(
        repo=repo,
        league_repo=league_repo,
        league_command_service=league_command_service,
        end_of_week_service=end_of_week_service,
        waiver_service=waiver_service
    )


class DevPubSubService:
    """Used for manually processing pub/sub messages while running in dev mode"""

    def __init__(
        self,
        repo: VirtualPubsubRepository,
        league_repo: LeagueRepository,
        league_command_service: LeagueCommandService,
        end_of_week_service: EndOfWeekService,
        waiver_service: WaiverService,
    ):
        self.repo = repo
        self.league_repo = league_repo
        self.league_command_service = league_command_service
        self.end_of_week_service = end_of_week_service
        self.waiver_service = waiver_service

    def process_pubsub_payloads(self) -> List[VirtualPubSubPayload]:
        payloads = self.repo.get_all()
        payloads.sort(key=lambda x: x.timestamp)

        for payload in payloads:
            handled = self.process_payload(payload)

            if handled:
                self.repo.delete(payload.id)

        if payloads:
            self.process_pubsub_payloads()  # reprocess until all payloads are complete
        else:
            return payloads

    def process_payload(self, payload: VirtualPubSubPayload) -> bool:
        if payload.topic == LEAGUE_COMMAND_TOPIC:
            push = PubSubPush(message=PubSubMessage(data=payload.data))
            leagues = self.league_repo.get_all()
            leagues = [league for league in leagues if league.is_active]
            Logger.info(f"Delivering league command to {len(leagues)} leagues")
            for league in leagues:
                self.league_command_service.execute_league_command(league.id, push)

            return True

        if payload.topic == END_OF_WEEK_TOPIC:
            Logger.info("Running end of week workflow")
            week_number = payload.data["completed_week_number"]
            self.end_of_week_service.run_workflow(week_number)
            return True

        if payload.topic == END_OF_WAIVERS_TOPIC:
            Logger.info("End of waivers (not used)")
            return True

        if payload.topic == LEAGUE_CREATED_TOPIC:
            Logger.info("League created (not handled in dev)")
            return True

        if payload.topic == UPDATE_PLAYERS_TOPIC:
            Logger.info("Call to update players (not handled in dev)")
            return True

        # unhandled
        return False
