from __future__ import annotations

from api.app.core.logging import Logger
from api.app.core.annotate_args import annotate_args

import logging
from abc import ABCMeta, abstractmethod
from typing import Generic, Optional, TypeVar

from pydantic import root_validator
from pydantic.main import BaseModel
from starlette_context import context

logger = logging.getLogger()


class BaseCommand(BaseModel):
    @property
    def request_user_id(self) -> Optional[str]:
        return context.data.get("user_id", None) if context.exists() else None


TCommand = TypeVar("TCommand", bound=BaseCommand)


@annotate_args
class BaseCommandResult(Generic[TCommand], BaseModel):
    command: TCommand
    error: Optional[str]
    success = True

    @root_validator
    def validate_success(cls, values):
        if "error" in values and values["error"]:
            values["success"] = False
        return values


TResult = TypeVar("TResult", bound=BaseModel)


class BaseCommandExecutor(Generic[TCommand, TResult], metaclass=ABCMeta):
    def execute(self, command: TCommand) -> TResult:
        name = type(self).__name__
        extra = {"command": command.json()}

        Logger.info(f"{name} executing", extra=extra)
        try:
            result = self.on_execute(command)
        except Exception as ex:
            Logger.error(f"Error executing {name}", exc_info=ex, extra=extra)
            raise ex

        Logger.info(f"{name} completed")

        return result

    @abstractmethod
    def on_execute(self, command: TCommand) -> TResult:
        raise NotImplementedError()
