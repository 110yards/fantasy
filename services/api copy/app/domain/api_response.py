from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    data: Any
    errors: list[dict] = []
    meta: dict = {}
