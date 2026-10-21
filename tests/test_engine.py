import pytest

from connect4.engine import (
    AI,
    COLS,
    EMPTY,
    HUMAN,
    ROWS,
    WINDOWS,
    Board,
    InvalidBoardError,
    InvalidMoveError,
    other,
)


def board_from_moves(moves: list[int]) -> Board:
    """Play columns alternately, starting with the human."""
    board = Board()
    player = HUMAN
    for col in moves:
        board = board.drop(col, player)
        player = other(player)
    return board


def test_new_board_is_empty():
    board = Board()
    assert board.count(HUMAN) == board.count(AI) == 0
    assert board.valid_moves() == list(range(COLS))
    assert board.winner() is None


def test_window_count():
    # 24 horizontal + 21 vertical + 12 + 12 diagonal lines on a 6x7 board
    assert len(WINDOWS) == 69


def test_drop_lands_on_bottom_and_stacks():
    board = Board().drop(3, HUMAN).drop(3, AI)
    assert board.grid[ROWS - 1][3] == HUMAN
    assert board.grid[ROWS - 2][3] == AI


def test_drop_does_not_mutate_original():
    board = Board()
    board.drop(0, HUMAN)
    assert board.grid[ROWS - 1][0] == EMPTY


def test_drop_rejects_out_of_range_and_full_columns():
    with pytest.raises(InvalidMoveError):
        Board().drop(COLS, HUMAN)
    with pytest.raises(InvalidMoveError):
        Board().drop(-1, HUMAN)
    full = board_from_moves([0] * ROWS)
    assert 0 not in full.valid_moves()
    with pytest.raises(InvalidMoveError):
        full.drop(0, HUMAN)


@pytest.mark.parametrize(
    ("moves", "expected_line"),
    [
        ([0, 0, 1, 1, 2, 2, 3], ((5, 0), (5, 1), (5, 2), (5, 3))),  # horizontal
        ([0, 1, 0, 1, 0, 1, 0], ((2, 0), (3, 0), (4, 0), (5, 0))),  # vertical
        ([0, 1, 1, 2, 2, 3, 2, 3, 3, 6, 3], ((2, 3), (3, 2), (4, 1), (5, 0))),  # diagonal /
    ],
)
def test_winner_detection(moves, expected_line):
    board = board_from_moves(moves)
    assert board.winner() == HUMAN
    assert board.winning_line() == expected_line
    assert board.is_terminal()


def test_draw_board_is_full_without_winner():
    # 21 pieces each, arranged so no four line up in any direction.
    rows = [
        [1, 2, 1, 2, 1, 2, 1],
        [1, 2, 1, 2, 1, 2, 1],
        [2, 1, 2, 1, 2, 1, 2],
        [2, 1, 2, 1, 2, 1, 2],
        [1, 2, 1, 2, 1, 2, 1],
        [2, 1, 2, 1, 2, 1, 2],
    ]
    board = Board.from_lists(rows)
    assert board.is_full()
    assert board.winner() is None
    assert board.is_terminal()


def test_from_lists_round_trip():
    board = board_from_moves([3, 3, 2])
    assert Board.from_lists(board.to_lists()) == board


@pytest.mark.parametrize(
    "rows",
    [
        [[0] * COLS] * (ROWS - 1),  # wrong row count
        [[0] * (COLS - 1)] * ROWS,  # wrong column count
        [[0] * COLS] * (ROWS - 1) + [[3] + [0] * (COLS - 1)],  # bad value
        [[1] + [0] * (COLS - 1)] + [[0] * COLS] * (ROWS - 1),  # floating piece
        [[0] * COLS] * (ROWS - 1) + [[2, 2] + [0] * (COLS - 2)],  # AI moved first
    ],
)
def test_from_lists_rejects_impossible_boards(rows):
    with pytest.raises(InvalidBoardError):
        Board.from_lists(rows)


def test_next_player_alternates():
    assert Board().next_player() == HUMAN
    assert Board().drop(0, HUMAN).next_player() == AI


def test_render_shows_pieces_and_column_numbers():
    text = Board().drop(0, HUMAN).drop(1, AI).render()
    lines = text.splitlines()
    assert lines[-1] == "0 1 2 3 4 5 6"
    assert lines[-2].startswith("X O")
