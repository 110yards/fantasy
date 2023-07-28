# from app.core.auth import require_role
from fastapi import Depends

from app.domain.commands.league.bid import BidCommand, BidCommandExecutor, create_bid_command_executor
from app.domain.commands.league.end_draft import EndDraftCommand, EndDraftCommandExecutor, create_end_draft_command_executor
from app.domain.commands.league.nominate_player import NominatePlayerCommand, NominatePlayerCommandExecutor, create_nominate_player_command_executor
from app.domain.commands.league.pass_bid import PassBidCommand, PassBidCommandExecutor, create_pass_bid_command_executor
from app.domain.commands.league.pause_resume_draft import PauseResumeDraftCommand, PauseResumeDraftCommandExecutor, create_pause_resume_draft_command_executor
from app.domain.commands.league.reset_draft import ResetDraftCommand, ResetDraftCommandExecutor, create_reset_draft_command_executor
from app.domain.commands.league.select_player import SelectPlayerCommand, SelectPlayerCommandExecutor, create_select_player_command_executor
from app.domain.commands.league.start_draft import StartDraftCommand, StartDraftCommandExecutor, create_start_draft_command_executor
from app.domain.commands.league.undo_last_draft_pick import (
    UndoLastDraftPickCommand,
    UndoLastDraftPickCommandExecutor,
    create_undo_last_draft_pick_command_executor,
)

from .api_router import APIRouter

router = APIRouter(prefix="/league/{league_id}/draft")


@router.post("/")
async def start_draft(league_id: str, command_executor: StartDraftCommandExecutor = Depends(create_start_draft_command_executor)):
    command = StartDraftCommand(league_id=league_id)
    return command_executor.execute(command)


@router.delete("/")
async def reset_draft(
    league_id: str,
    command_executor: ResetDraftCommandExecutor = Depends(create_reset_draft_command_executor),
):
    command = ResetDraftCommand(league_id=league_id)
    return command_executor.execute(command)


@router.post("/end")
async def end_draft(
    league_id: str,
    command_executor: EndDraftCommandExecutor = Depends(create_end_draft_command_executor),
):
    command = EndDraftCommand(league_id=league_id)
    return command_executor.execute(command)


@router.post("/nominate")
async def nominate(command: NominatePlayerCommand, command_executor: NominatePlayerCommandExecutor = Depends(create_nominate_player_command_executor)):
    return command_executor.execute(command)


@router.post("/bid")
async def bid(command: BidCommand, command_executor: BidCommandExecutor = Depends(create_bid_command_executor)):
    return command_executor.execute(command)


@router.post("/pass")
async def pass_bid(command: PassBidCommand, command_executor: PassBidCommandExecutor = Depends(create_pass_bid_command_executor)):
    return command_executor.execute(command)


@router.post("/pause")
async def pause_draft(league_id: str, command_executor: PauseResumeDraftCommandExecutor = Depends(create_pause_resume_draft_command_executor)):
    command = PauseResumeDraftCommand(league_id=league_id, pause=True)
    return command_executor.execute(command)


@router.post("/resume")
async def resume_draft(league_id: str, command_executor: PauseResumeDraftCommandExecutor = Depends(create_pause_resume_draft_command_executor)):
    command = PauseResumeDraftCommand(league_id=league_id, pause=False)
    return command_executor.execute(command)


@router.post("/undo")
async def undo_last_pick(league_id: str, command_executor: UndoLastDraftPickCommandExecutor = Depends(create_undo_last_draft_pick_command_executor)):
    command = UndoLastDraftPickCommand(league_id=league_id)
    return command_executor.execute(command)


@router.post("/select_player")
async def select_player(command: SelectPlayerCommand, command_executor: SelectPlayerCommandExecutor = Depends(create_select_player_command_executor)):
    return command_executor.execute(command)
