from api.app.domain.enums.draft_state import DraftState
from typing import Optional

from api.app.core.annotate_args import annotate_args
from api.app.core.base_command_executor import (BaseCommand, BaseCommandExecutor,
                                                BaseCommandResult)
from api.app.domain.repositories.league_config_repository import (
    LeagueConfigRepository, create_league_config_repository)
from api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from fastapi import Depends
from firebase_admin import firestore


def create_update_league_positions_command_executor(
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository)
):
    return UpdateLeaguePositionsCommandExecutor(league_repo, league_config_repo)


@annotate_args
class UpdateLeaguePositionsCommand(BaseCommand):
    league_id: Optional[str]
    qb: int
    rb: int
    wr: int
    k: int
    lb: int
    dl: int
    db: int
    o_flex: int
    d_flex: int
    flex: int
    ir: int
    bye: int
    bench: int
    allow_bench_qb: bool
    allow_bench_rb: bool
    allow_bench_k: bool


@annotate_args
class UpdateLeaguePositionsResult(BaseCommandResult[UpdateLeaguePositionsCommand]):
    pass


class UpdateLeaguePositionsCommandExecutor(BaseCommandExecutor[UpdateLeaguePositionsCommand, UpdateLeaguePositionsResult]):

    def __init__(self,
                 league_repo: LeagueRepository,
                 league_config_repo: LeagueConfigRepository):
        self.league_repo = league_repo
        self.league_config_repo = league_config_repo

    def on_execute(self, command: UpdateLeaguePositionsCommand) -> UpdateLeaguePositionsResult:

        league = self.league_repo.get(command.league_id)

        if league.draft_state != DraftState.NOT_STARTED:
            return UpdateLeaguePositionsResult(command=command, error="Positions cannot be updated after draft has started")

        positions = self.league_config_repo.get_positions_config(command.league_id)

        positions.qb = command.qb
        positions.rb = command.rb
        positions.wr = command.wr
        positions.k = command.k
        positions.lb = command.lb
        positions.dl = command.dl
        positions.db = command.db
        positions.o_flex = command.o_flex
        positions.d_flex = command.d_flex
        positions.flex = command.flex
        positions.ir = command.ir
        positions.bye = command.bye
        positions.bench = command.bench
        positions.allow_bench_qb = command.allow_bench_qb
        positions.allow_bench_rb = command.allow_bench_rb
        positions.allow_bench_k = command.allow_bench_k

        league.positions = positions.create_positions()

        @firestore.transactional
        def update(transaction):
            self.league_repo.update(league, transaction)
            self.league_config_repo.set_positions_config(league.id, positions, transaction)

        transaction = self.league_repo.firestore.create_transaction()
        update(transaction)

        return UpdateLeaguePositionsResult(command=command)
