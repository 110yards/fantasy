from typing import Any

from pydantic import BaseModel


class CommandResult(BaseModel):
    success: bool
    message: str
    data: Any = None

    @staticmethod
    def success_result(message: str = "Success", data: Any = None) -> "CommandResult":
        return CommandResult(success=True, message=message, data=data)

    @staticmethod
    def failure_result(message: str) -> "CommandResult":
        return CommandResult(success=False, message=message)
