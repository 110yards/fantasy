from typing import Optional

from fastapi import FastAPI
from fastapi.param_functions import Depends
from starlette.middleware import Middleware
from starlette_context.middleware.context_middleware import ContextMiddleware
from starlette_context.plugins.correlation_id import CorrelationIdPlugin
from starlette_context.plugins.request_id import RequestIdPlugin
from strivelogger import StriveLogger
from strivelogger.logger_implementations.uvicorn_logger import UvicornLogger

from app.config.settings import Settings, get_settings
from app.core.initialize_firebase import initialize_firebase
from app.domain.cqrs.commands.upsert_players_command import UpsertPlayersCommand
from app.domain.cqrs.commands.upsert_schedule_command import UpsertScheduleCommand
from app.domain.cqrs.executors.upsert_players_executor import (
    UpsertPlayersExecutor,
    create_upsert_players_executor,
)
from app.domain.cqrs.executors.upsert_schedule_executor import (
    UpsertScheduleExecutor,
    create_upsert_schedule_executor,
)
from app.domain.services.player_service import PlayerService, create_player_service
from app.domain.services.schedule_service import (
    ScheduleService,
    create_schedule_service,
)
from app.middleware.api_key_auth_middleware import ApiKeyAuthMiddleware
from app.middleware.logging_middleware import LoggingMiddleware

from .domain.cqrs.commands.upsert_boxscores_command import UpsertBoxscoresCommand
from .domain.cqrs.commands.upsert_scoreboard_command import UpsertScoreboardCommand
from .domain.cqrs.executors.upsert_boxscores_executor import UpsertBoxscoresExecutor, create_upsert_boxscores_executor
from .domain.cqrs.executors.upsert_scoreboard_executor import UpsertScoreboardExecutor, create_upsert_scoreboard_executor
from .domain.services.active_boxscores_service import ActiveBoxscoresService, create_active_boxscores_service
from .domain.services.final_boxscores_service import FinalBoxscoresService, create_final_boxscores_service
from .domain.services.scoreboard_service import ScoreboardService, create_scoreboard_service

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


@app.get("/")
async def root(settings: Settings = Depends(get_settings)):
    return {"status": "ok", "version": settings.version}


@app.get("/schedule")
async def get_schedule(service: ScheduleService = Depends(create_schedule_service)):
    return service.get_schedule()


@app.post("/schedule")
async def upsert_schedule(executor: UpsertScheduleExecutor = Depends(create_upsert_schedule_executor)):
    return executor.execute(UpsertScheduleCommand())


@app.get("/boxscores/active")
async def get_active_boxscores(service: ActiveBoxscoresService = Depends(create_active_boxscores_service)):
    return service.get_boxscores()


@app.post("/boxscores/active")
async def upsert_active_boxscores(
    service: ActiveBoxscoresService = Depends(create_active_boxscores_service),
    executor: UpsertBoxscoresExecutor = Depends(create_upsert_boxscores_executor),
):
    boxscores = service.get_boxscores()
    return executor.execute(UpsertBoxscoresCommand(boxscores=boxscores))


@app.get("/boxscores/final")
async def get_final_boxscores(year: Optional[int] = None, service: FinalBoxscoresService = Depends(create_final_boxscores_service)):
    return service.get_boxscores(year)


@app.post("/boxscores/final")
async def upsert_final_boxscores(
    year: Optional[int] = None,
    service: FinalBoxscoresService = Depends(create_final_boxscores_service),
    executor: UpsertBoxscoresExecutor = Depends(create_upsert_boxscores_executor),
):
    boxscores = service.get_boxscores(year)
    return executor.execute(UpsertBoxscoresCommand(boxscores=boxscores))


@app.get("/players")
async def get_players(service: PlayerService = Depends(create_player_service)):
    return service.get_players()


@app.post("/players")
async def upsert_players(executor: UpsertPlayersExecutor = Depends(create_upsert_players_executor)):
    return executor.execute(UpsertPlayersCommand())


@app.get("/scoreboard")
async def get_scoreboard(service: ScoreboardService = Depends(create_scoreboard_service)):
    return service.get_scoreboard()


@app.post("/scoreboard")
async def upsert_scoreboard(
    executor: UpsertScoreboardExecutor = Depends(create_upsert_scoreboard_executor),
):
    return executor.execute(UpsertScoreboardCommand())
