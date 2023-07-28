from fastapi import Depends
from pydantic import BaseModel

from app.config import settings
from app.core import firebase

from .api_router import APIRouter

router = APIRouter(prefix="/login")


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/")
async def login(request: LoginRequest, settings: settings.Settings = Depends(settings.get_settings)):
    return firebase.login(request.email, request.password, settings)
