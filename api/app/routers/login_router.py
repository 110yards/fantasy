from api.app.config import settings
from yards_py.core import firebase
from fastapi import Depends

from api.app.domain.repositories.user_repository import create_user_repository
from .api_router import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/login")


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/")
async def login(request: LoginRequest, settings: settings.Settings = Depends(settings.get_settings)):
    create_user_repository()
    return firebase.login(request.email, request.password, settings)
