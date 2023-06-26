from app.config import settings
from app.yards_py.core import firebase
from fastapi import Depends

from .api_router import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/login")


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/")
async def login(request: LoginRequest, settings: settings.Settings = Depends(settings.get_settings)):
    return firebase.login(request.email, request.password, settings)
