import firebase_admin
from fastapi import Depends, FastAPI
from starlette.middleware import Middleware
from starlette_context.middleware.context_middleware import ContextMiddleware
from starlette_context.plugins.correlation_id import CorrelationIdPlugin
from starlette_context.plugins.request_id import RequestIdPlugin

from services.system.app.config.settings import Settings, get_settings
from services.system.app.routers import (
    dev_router,
    import_router,
    league_router,
    logging_router,
    migration_router,
    system_router,
)
from yards_py.core.logging import Logger
from yards_py.middleware.api_key_auth_middleware import ApiKeyAuthMiddleware
from yards_py.middleware.logging_middleware import LoggingMiddleware

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

app.include_router(migration_router.router)
app.include_router(system_router.router)
app.include_router(logging_router.router)
app.include_router(league_router.router)
app.include_router(import_router.router)
if settings.is_dev():
    app.include_router(dev_router.router)

firebase_admin.initialize_app(options={"projectId": settings.gcloud_project})

Logger.info("System service started")


@app.get("/")
async def root(settings: Settings = Depends(get_settings)):
    return {"status": "ok", "version": settings.version}
