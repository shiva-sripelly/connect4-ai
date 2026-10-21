"""Connect Four game rules.

The board is immutable: every move returns a new ``Board``. Row 0 is the top
row, so pieces fall toward higher row indexes.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

ROWS = 6
COLS = 7
CONNECT = 4

EMPTY = 0
HUMAN = 1
AI = 2
PLAYERS = (HUMAN, AI)

Cell = tuple[int, int]
Grid = tuple[tuple[int, ...], ...]


class InvalidMoveError(ValueError):
    """Raised when a move is outside the board or into a full column."""


class InvalidBoardError(ValueError):
    """Raised when a board cannot occur in a real game."""


def other(player: int) -> int:
    """Return the opponent of ``player``."""
    if player not in PLAYERS:
        raise ValueError(f"Unknown player: {player}")
    return AI if player == HUMAN else HUMAN


def _build_windows() -> tuple[tuple[Cell, ...], ...]:
    """Every line of four cells on the board, in all four directions."""
    directions = ((0, 1), (1, 0), (1, 1), (1, -1))
    windows: list[tuple[Cell, ...]] = []
    for row in range(ROWS):
        for col in range(COLS):
            for d_row, d_col in directions:
                end_row = row + d_row * (CONNECT - 1)
                end_col = col + d_col * (CONNECT - 1)
                if 0 <= end_row < ROWS and 0 <= end_col < COLS:
                    windows.append(
                        tuple((row + d_row * i, col + d_col * i) for i in range(CONNECT))
                    )
    return tuple(windows)


WINDOWS = _build_windows()


def _empty_grid() -> Grid:
    return tuple(tuple(EMPTY for _ in range(COLS)) for _ in range(ROWS))


@dataclass(frozen=True)
class Board:
    grid: Grid = field(default_factory=_empty_grid)

    @classmethod
    def from_lists(cls, rows: Sequence[Sequence[int]]) -> Board:
        """Build a board from nested lists and check that it is a legal position."""
        if len(rows) != ROWS or any(len(row) != COLS for row in rows):
            raise InvalidBoardError(f"Board must be {ROWS} rows x {COLS} columns")

        grid: Grid = tuple(tuple(int(cell) for cell in row) for row in rows)
        if any(cell not in (EMPTY, *PLAYERS) for row in grid for cell in row):
            raise InvalidBoardError("Cells must be 0 (empty), 1 (human) or 2 (AI)")

        for col in range(COLS):
            seen_piece = False
            for row in range(ROWS):
                if grid[row][col] != EMPTY:
                    seen_piece = True
                elif seen_piece:
                    raise InvalidBoardError(f"Floating piece in column {col}")

        board = cls(grid)
        human, ai = board.count(HUMAN), board.count(AI)
        if human - ai not in (0, 1):
            raise InvalidBoardError("Piece counts are impossible (human moves first)")
        return board

    def to_lists(self) -> list[list[int]]:
        return [list(row) for row in self.grid]

    def count(self, player: int) -> int:
        return sum(row.count(player) for row in self.grid)

    def valid_moves(self) -> list[int]:
        return [col for col in range(COLS) if self.grid[0][col] == EMPTY]

    def next_player(self) -> int:
        return HUMAN if self.count(HUMAN) == self.count(AI) else AI

    def drop(self, col: int, player: int) -> Board:
        """Return a new board with ``player``'s piece dropped into ``col``."""
        if player not in PLAYERS:
            raise ValueError(f"Unknown player: {player}")
        if not 0 <= col < COLS:
            raise InvalidMoveError(f"Column {col} is outside the board")
        for row in range(ROWS - 1, -1, -1):
            if self.grid[row][col] == EMPTY:
                new_row = self.grid[row][:col] + (player,) + self.grid[row][col + 1 :]
                return Board(self.grid[:row] + (new_row,) + self.grid[row + 1 :])
        raise InvalidMoveError(f"Column {col} is full")

    def winning_line(self) -> tuple[Cell, ...] | None:
        for window in WINDOWS:
            first = self.grid[window[0][0]][window[0][1]]
            if first != EMPTY and all(self.grid[r][c] == first for r, c in window):
                return window
        return None

    def winner(self) -> int | None:
        line = self.winning_line()
        return None if line is None else self.grid[line[0][0]][line[0][1]]

    def is_full(self) -> bool:
        return not self.valid_moves()

    def is_terminal(self) -> bool:
        return self.winner() is not None or self.is_full()

    def render(self) -> str:
        symbols = {EMPTY: ".", HUMAN: "X", AI: "O"}
        lines = [" ".join(symbols[cell] for cell in row) for row in self.grid]
        lines.append(" ".join(str(col) for col in range(COLS)))
        return "\n".join(lines)
