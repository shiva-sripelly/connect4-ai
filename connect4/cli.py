"""Play Connect Four in the terminal: python -m connect4"""

from __future__ import annotations

import argparse

from .ai import DIFFICULTY_DEPTH, best_move
from .engine import AI, HUMAN, Board, InvalidMoveError


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Play Connect Four against the AI.")
    parser.add_argument("--difficulty", choices=DIFFICULTY_DEPTH, default="hard")
    args = parser.parse_args(argv)
    depth = DIFFICULTY_DEPTH[args.difficulty]

    board = Board()
    print("You are X. Enter a column number (0-6), or q to quit.\n")
    while not board.is_terminal():
        print(board.render(), "\n")
        choice = input("Your move: ").strip().lower()
        if choice == "q":
            print("Bye!")
            return
        try:
            board = board.drop(int(choice), HUMAN)
        except (ValueError, InvalidMoveError) as exc:
            print(f"Invalid move: {exc}\n")
            continue
        if board.is_terminal():
            break
        col = best_move(board, AI, depth)
        board = board.drop(col, AI)
        print(f"AI plays column {col}\n")

    print(board.render(), "\n")
    winner = board.winner()
    print("You win!" if winner == HUMAN else "AI wins!" if winner == AI else "It's a draw!")


if __name__ == "__main__":
    main()
