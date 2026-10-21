"""Connect Four AI: negamax search with alpha-beta pruning."""

from __future__ import annotations

import math

from .engine import AI, COLS, EMPTY, WINDOWS, Board, other

WIN_SCORE = 1_000_000
# Search center columns first: they are usually stronger, and good move
# ordering makes alpha-beta pruning far more effective.
MOVE_ORDER = sorted(range(COLS), key=lambda col: abs(col - COLS // 2))

DIFFICULTY_DEPTH = {"easy": 1, "medium": 3, "hard": 6}


def _score_window(values: list[int], player: int) -> int:
    mine = values.count(player)
    theirs = values.count(other(player))
    empty = values.count(EMPTY)
    if mine == 3 and empty == 1:
        return 5
    if mine == 2 and empty == 2:
        return 2
    if theirs == 3 and empty == 1:
        return -4
    return 0


def evaluate(board: Board, player: int) -> int:
    """Heuristic score of a non-terminal position, from ``player``'s view."""
    center = COLS // 2
    score = 3 * sum(1 for row in board.grid if row[center] == player)
    for window in WINDOWS:
        score += _score_window([board.grid[r][c] for r, c in window], player)
    return score


def _negamax(board: Board, depth: int, alpha: float, beta: float, player: int, ply: int) -> float:
    if board.winner() is not None:
        # The opponent made the last move, so a finished game is a loss for
        # ``player``. Losses found later (higher ply) are less bad.
        return -(WIN_SCORE - ply)
    if board.is_full():
        return 0
    if depth == 0:
        return evaluate(board, player)

    best = -math.inf
    for col in MOVE_ORDER:
        if col not in board.valid_moves():
            continue
        child = board.drop(col, player)
        score = -_negamax(child, depth - 1, -beta, -alpha, other(player), ply + 1)
        best = max(best, score)
        alpha = max(alpha, score)
        if alpha >= beta:
            break
    return best


def best_move(board: Board, player: int = AI, depth: int = DIFFICULTY_DEPTH["hard"]) -> int:
    """Return the best column for ``player``. Ties go to the more central column."""
    if depth < 1:
        raise ValueError("depth must be at least 1")
    if board.is_terminal():
        raise ValueError("Game is already over")

    best_col = -1
    best_score = -math.inf
    alpha, beta = -math.inf, math.inf
    for col in MOVE_ORDER:
        if col not in board.valid_moves():
            continue
        child = board.drop(col, player)
        score = -_negamax(child, depth - 1, -beta, -alpha, other(player), 1)
        if score > best_score:
            best_score, best_col = score, col
        alpha = max(alpha, score)
    return best_col
