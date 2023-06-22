from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.param_functions import Depends
from starlette.middleware import Middleware
from starlette_context.middleware.context_middleware import ContextMiddleware
from starlette_context.plugins.correlation_id import CorrelationIdPlugin
from starlette_context.plugins.request_id import RequestIdPlugin
from strivelogger import StriveLogger
from strivelogger.logger_implementations.uvicorn_logger import UvicornLogger

from app.config.settings import Settings, get_settings
from app.core.initialize_firebase import initialize_firebase
from app.domain.services.games_service import GamesService, create_games_service
from app.domain.services.injuries_service import (
    InjuriesService,
    create_injuries_service,
)
from app.domain.services.players_service import PlayersService, create_players_service
from app.middleware.api_key_auth_middleware import ApiKeyAuthMiddleware
from app.middleware.logging_middleware import LoggingMiddleware

settings = get_settings()
ApiKeyAuthMiddleware.setup(key=settings.api_key, anonymous_routes=["/"])

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

initialize_firebase(settings)

StriveLogger.info("Importer started")


@app.get("/")
async def root(settings: Settings = Depends(get_settings)):
    return {"status": "ok", "version": settings.version}


@app.get("/games/{year}/game/{game_id}")
async def game(
    year: int,
    game_id: str,
    service: GamesService = Depends(create_games_service),
):
    return service.get_game(year, game_id)


@app.get("/games/{year}")
async def games(
    year: int,
    service: GamesService = Depends(create_games_service),
):
    return service.get_games(year)


@app.get("/players")
async def players(
    request: Request,
    service: PlayersService = Depends(create_players_service),
):
    year = request.query_params.get("filter[season][eq]", datetime.now().year)

    return service.get_players(year)


@app.get("/players/{player_id}")
async def player(
    player_id: str,
    year: Optional[int] = None,
    service: PlayersService = Depends(create_players_service),
):
    year = year or datetime.now().year
    return service.get_player(year, player_id)


@app.get("/injuries")
async def injuries(
    service: InjuriesService = Depends(create_injuries_service),
):
    return service.get_injuries()
