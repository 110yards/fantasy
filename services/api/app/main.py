from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.param_functions import Depends

from services.api.app.config.settings import Settings, get_settings
from yards_py.core.initialize_firebase import initialize_firebase
from yards_py.core.logging import Logger
from services.api.app.middleware.config import app_middleware
from services.api.app.routers import (
    admin_router,
    league_draft_router,
    league_router,
    logging_router,
    login_router,
    migration_router,
    projection_router,
    roster_router,
    user_router,
    dev_router,
)

app = FastAPI(middleware=app_middleware)

settings = get_settings()
Logger.initialize(settings.is_dev(), settings.gcloud_project, settings.service_name, settings.region)

origins = settings.origins.split(";")
app.add_middleware(CORSMiddleware,
                   allow_headers="*",
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"])

app.include_router(league_router.router)
app.include_router(league_draft_router.router)
app.include_router(login_router.router)
app.include_router(user_router.router)
app.include_router(roster_router.router)
app.include_router(logging_router.router)
app.include_router(admin_router.router)
app.include_router(migration_router.router)
app.include_router(projection_router.router)
if settings.is_dev():
    app.include_router(dev_router.router)

initialize_firebase(settings.rtdb_emulator_host, settings.gcloud_project)


@app.get("/")
async def root(settings: Settings = Depends(get_settings)):
    return {
        "status": "ok",
        "version": settings.version
    }
