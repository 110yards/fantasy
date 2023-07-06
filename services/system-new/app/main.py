from fastapi import Depends, FastAPI
from starlette.middleware import Middleware
from starlette_context.middleware.context_middleware import ContextMiddleware
from starlette_context.plugins.correlation_id import CorrelationIdPlugin
from starlette_context.plugins.request_id import RequestIdPlugin
from strivelogger import StriveLogger
from strivelogger.logger_implementations.uvicorn_logger import UvicornLogger

from app.config.settings import get_settings
from app.core.initialize_firebase import initialize_firebase
from app.middleware.api_key_auth_middleware import ApiKeyAuthMiddleware
from app.middleware.logging_middleware import LoggingMiddleware

from .domain.services.end_of_day_service import EndOfDayService, create_end_of_day_service

settings = get_settings()

ApiKeyAuthMiddleware.setup(key=settings.api_key, anonymous_routes=[""])

app = FastAPI(
    middleware=[
        Middleware(
            ContextMiddleware,
            plugins=(
                RequestIdPlugin(),
                CorrelationIdPlugin(),
            ),
        ),
        Middleware(LoggingMiddleware),
        Middleware(ApiKeyAuthMiddleware),
    ]
)

logger = UvicornLogger()

StriveLogger.initialize(logger=logger)

initialize_firebase(settings.rtdb_emulator_host, settings.gcloud_project)

StriveLogger.info("Importer started")


@app.post("/end_of_day")
async def end_of_day(service: EndOfDayService = Depends(create_end_of_day_service)):
    service.run_workflow()


# @app.post("/end_of_week")
# async def end_of_week(
#     push: PubSubPush,
#     service: EndOfWeekService = Depends(create_end_of_week_service)
# ):
#     push_data = push.get_data()
#     request = EndOfWeekRequest(**push_data)
#     return service.run_workflow(request.completed_week_number)


# @app.post("/league_command")
# async def league_command(
#     league_id: str,
#     push: PubSubPush,
#     league_command_service: LeagueCommandService = Depends(create_league_command_service)
# ):
#     return league_command_service.execute_league_command(league_id, push)

# if settings.is_dev:

#     @app.post("/pubsub")
#     async def pubsub(
#         service: DevPubSubService = Depends(create_dev_pubsub_service),
#     ):
#         return service.process_pubsub_payloads()
