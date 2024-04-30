from fastapi import Depends

from yards_py.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from yards_py.domain.entities.scheduled_game import ScheduledGame
from yards_py.domain.repositories.scheduled_game_repository import ScheduledGameRepository, create_scheduled_game_repository


class ImportScheduleCommand(BaseCommand):
    data: dict


class ImportScheduleResult(BaseCommandResult[ImportScheduleCommand]):
    pass


class ImportScheduleCommandExecutor(BaseCommandExecutor[ImportScheduleCommand, ImportScheduleResult]):
    def __init__(self, repo: ScheduledGameRepository):
        self.repo = repo

    def on_execute(self, command: ImportScheduleCommand) -> ImportScheduleResult:
        year = command.data.get("year")
        games = command.data.get("games")

        scheduled_games = [ScheduledGame.from_core(year, x) for x in games]

        for game in scheduled_games:
            self.repo.set(year, game)

        return ImportScheduleResult(command=command)


def create_import_schedule_command_executor(
    repo: ScheduledGameRepository = Depends(create_scheduled_game_repository),
):
    return ImportScheduleCommandExecutor(repo=repo)
