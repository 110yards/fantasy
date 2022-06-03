
from .api_router import APIRouter
from yards_py.core.logging import Logger

router = APIRouter(prefix="/log")


@router.post("/debug")
async def debug():
    Logger.debug("This is a test debugging log entry")
    Logger.debug("This is a test debugging log entry with extra info", extra={"foo": "bar"})
    return {"logger": Logger.logger_type()}


@router.post("/info")
async def info():
    Logger.info("This is a test info log entry")
    Logger.info("This is a test info log entry with extra info", extra={"foo": "bar"})
    return {"logger": Logger.logger_type()}


@router.post("/warn")
async def warn():
    Logger.warn("This is a test warn log entry")
    Logger.warn("This is a test warn log entry with extra info", extra={"foo": "bar"})
    return {"logger": Logger.logger_type()}


@router.post("/error")
async def error():
    Logger.error("This is a test error log entry")
    try:
        raise NotImplementedError()
    except Exception as ex:
        Logger.error("This is a test error log entry with extra info", ex)
    return {"logger": Logger.logger_type()}


@router.post("/exception")
async def exception():
    assert not True
