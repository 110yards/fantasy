import firebase_admin
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.param_functions import Depends

from api.app.config.settings import Settings, get_settings
from api.app.core.logging import Logger
from api.app.middleware.config import app_middleware
from api.app.routers import (
    admin_router,
    league_draft_router,
    league_router,
    logging_router,
    login_router,
    migration_router,
    projection_router,
    roster_router,
    score_router,
    system_router,
    user_router
)

app = FastAPI(middleware=app_middleware)

settings = get_settings()
Logger.initialize(settings)

origins = settings.origins.split(";")
app.add_middleware(CORSMiddleware,
                   allow_headers="*",
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"])

app.include_router(system_router.router)
app.include_router(league_router.router)
app.include_router(league_draft_router.router)
app.include_router(login_router.router)
app.include_router(user_router.router)
app.include_router(roster_router.router)
app.include_router(logging_router.router)
app.include_router(admin_router.router)
app.include_router(migration_router.router)
app.include_router(projection_router.router)
app.include_router(score_router.router)

firebase_admin.initialize_app(options={"projectId": settings.gcloud_project})


@app.get("/")
async def root(settings: Settings = Depends(get_settings)):
    return {
        "status": "ok",
        "version": settings.version
    }
