"""FastAPI backend. The API is stateless: the client sends the whole board."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .ai import DIFFICULTY_DEPTH, best_move
from .engine import AI, COLS, HUMAN, Board, InvalidBoardError, InvalidMoveError

STATIC_DIR = Path(__file__).parent / "static"

Status = Literal["in_progress", "human_won", "ai_won", "draw"]

app = FastAPI(title="Connect Four AI", version="1.0.0")


class MoveRequest(BaseModel):
    board: list[list[int]] = Field(description="6x7 grid; 0 empty, 1 human, 2 AI; row 0 is the top")
    column: int = Field(ge=0, lt=COLS, description="Column the human plays")
    difficulty: Literal["easy", "medium", "hard"] = "hard"


class MoveResponse(BaseModel):
    board: list[list[int]]
    human_move: int
    ai_move: int | None
    status: Status
    winning_line: list[list[int]] | None


def _status(board: Board) -> Status:
    winner = board.winner()
    if winner == HUMAN:
        return "human_won"
    if winner == AI:
        return "ai_won"
    return "draw" if board.is_full() else "in_progress"


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/move", response_model=MoveResponse)
def move(request: MoveRequest) -> MoveResponse:
    try:
        board = Board.from_lists(request.board)
    except InvalidBoardError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if board.is_terminal():
        raise HTTPException(status_code=400, detail="Game is already over")
    if board.next_player() != HUMAN:
        raise HTTPException(status_code=400, detail="It is not the human's turn")

    try:
        board = board.drop(request.column, HUMAN)
    except InvalidMoveError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    ai_move = None
    if not board.is_terminal():
        ai_move = best_move(board, AI, DIFFICULTY_DEPTH[request.difficulty])
        board = board.drop(ai_move, AI)

    line = board.winning_line()
    return MoveResponse(
        board=board.to_lists(),
        human_move=request.column,
        ai_move=ai_move,
        status=_status(board),
        winning_line=[list(cell) for cell in line] if line else None,
    )


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
