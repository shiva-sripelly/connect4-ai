import random

import pytest

from connect4.ai import DIFFICULTY_DEPTH, best_move, evaluate
from connect4.engine import AI, HUMAN, Board, other


def play(board: Board, moves: list[tuple[int, int]]) -> Board:
    for col, player in moves:
        board = board.drop(col, player)
    return board


def test_first_move_is_center():
    board = Board().drop(0, HUMAN)
    assert best_move(board, AI, depth=4) == 3


@pytest.mark.parametrize("depth", [1, 3, 5])
def test_takes_immediate_win(depth):
    # AI has three in column 6; human has scattered pieces.
    board = play(Board(), [(0, HUMAN), (6, AI), (1, HUMAN), (6, AI), (3, HUMAN), (6, AI), (0, HUMAN)])
    assert best_move(board, AI, depth) == 6


@pytest.mark.parametrize("depth", [2, 3, 5])
def test_blocks_immediate_loss(depth):
    # Human threatens to complete the bottom row at column 3.
    board = play(Board(), [(0, HUMAN), (6, AI), (1, HUMAN), (6, AI), (2, HUMAN)])
    assert best_move(board, AI, depth) == 3


def test_returns_only_valid_columns():
    board = Board()
    player = HUMAN
    for col in [0, 0, 0, 0, 0, 0]:  # fill column 0
        board = board.drop(col, player)
        player = other(player)
    assert best_move(board, HUMAN, depth=3) != 0


def test_raises_when_game_is_over():
    board = play(Board(), [(0, HUMAN), (1, AI), (0, HUMAN), (1, AI), (0, HUMAN), (1, AI), (0, HUMAN)])
    with pytest.raises(ValueError):
        best_move(board, AI)


def test_rejects_invalid_depth():
    with pytest.raises(ValueError):
        best_move(Board(), AI, depth=0)


def test_evaluate_rewards_center_control():
    center = Board().drop(3, AI)
    edge = Board().drop(0, AI)
    assert evaluate(center, AI) > evaluate(edge, AI)


def test_deterministic():
    board = play(Board(), [(3, HUMAN), (3, AI), (2, HUMAN)])
    assert len({best_move(board, AI, 4) for _ in range(3)}) == 1


def test_medium_ai_beats_random_player():
    rng = random.Random(42)
    results = {"ai": 0, "random": 0, "draw": 0}
    for _ in range(10):
        board = Board()
        while not board.is_terminal():
            board = board.drop(rng.choice(board.valid_moves()), HUMAN)
            if board.is_terminal():
                break
            board = board.drop(best_move(board, AI, DIFFICULTY_DEPTH["medium"]), AI)
        winner = board.winner()
        results["ai" if winner == AI else "random" if winner == HUMAN else "draw"] += 1
    assert results["random"] == 0
    assert results["ai"] >= 9
