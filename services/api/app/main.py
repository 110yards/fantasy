from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.param_functions import Depends

from app.config.settings import Settings, get_settings
from app.core.initialize_firebase import initialize_firebase
from app.core.logging import Logger
from app.middleware.config import app_middleware
from app.routers import (
    admin_router,
    dev_router,
    league_draft_router,
    league_router,
    logging_router,
    login_router,
    migration_router,
    mod_router,
    news_router,
    projection_router,
    roster_router,
    user_router,
)

app = FastAPI(middleware=app_middleware)

settings = get_settings()
Logger.initialize(settings.is_dev(), settings.gcloud_project, settings.service_name, settings.region)

origins = settings.origins.split(";")
app.add_middleware(
    CORSMiddleware,
    allow_headers="*",
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
)

app.include_router(league_router.router)
app.include_router(league_draft_router.router)
app.include_router(login_router.router)
app.include_router(user_router.router)
app.include_router(roster_router.router)
app.include_router(logging_router.router)
app.include_router(admin_router.router)
app.include_router(migration_router.router)
app.include_router(projection_router.router)
app.include_router(news_router.router)
app.include_router(mod_router.router)

if settings.is_dev():
    app.include_router(dev_router.router)

initialize_firebase(settings.rtdb_emulator_host, settings.gcloud_project)


@app.get("/")
async def root(settings: Settings = Depends(get_settings)):
    return {"status": "ok", "version": settings.version}
