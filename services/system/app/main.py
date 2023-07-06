from app.config.settings import Settings, get_settings
from app.routers import (
    dev_router,
    league_router,
    migration_router,
    system_router,
)
from app.yards_py.core.logging import Logger
from app.yards_py.middleware.api_key_auth_middleware import ApiKeyAuthMiddleware
from app.yards_py.middleware.logging_middleware import LoggingMiddleware
from fastapi import FastAPI
from fastapi.param_functions import Depends
from starlette.middleware import Middleware
from starlette_context.middleware.context_middleware import ContextMiddleware
from starlette_context.plugins.correlation_id import CorrelationIdPlugin
from starlette_context.plugins.request_id import RequestIdPlugin

from .yards_py.core.initialize_firebase import initialize_firebase

settings = get_settings()
ApiKeyAuthMiddleware.setup(settings.api_key, anonymous_routes=[""])

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
Logger.initialize(settings.is_dev, settings.gcloud_project, settings.service_name, settings.region)
initialize_firebase(settings.rtdb_emulator_host, settings.gcloud_project)

app.include_router(migration_router.router)
app.include_router(system_router.router)
app.include_router(league_router.router)
if settings.is_dev():
    app.include_router(dev_router.router)


Logger.info("System service started")


@app.get("/")
async def root(settings: Settings = Depends(get_settings)):
    return {"status": "ok", "version": settings.version}
