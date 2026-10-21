import pytest
from fastapi.testclient import TestClient

from connect4.api import app
from connect4.engine import AI, COLS, HUMAN, ROWS, Board

client = TestClient(app)


def empty() -> list[list[int]]:
    return Board().to_lists()


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_index_serves_web_ui():
    res = client.get("/")
    assert res.status_code == 200
    assert "Connect Four AI" in res.text


def test_move_plays_human_then_ai():
    res = client.post("/api/move", json={"board": empty(), "column": 0})
    assert res.status_code == 200
    data = res.json()
    board = Board.from_lists(data["board"])
    assert data["human_move"] == 0
    assert data["ai_move"] == 3
    assert data["status"] == "in_progress"
    assert data["winning_line"] is None
    assert board.count(HUMAN) == board.count(AI) == 1


def test_ai_win_reports_status_and_line():
    board = Board()
    for col, player in [(0, HUMAN), (6, AI), (1, HUMAN), (6, AI), (3, HUMAN), (6, AI)]:
        board = board.drop(col, player)
    res = client.post("/api/move", json={"board": board.to_lists(), "column": 0})
    data = res.json()
    assert data["ai_move"] == 6
    assert data["status"] == "ai_won"
    assert len(data["winning_line"]) == 4


def test_human_win_skips_ai_move():
    board = Board()
    for col, player in [(0, HUMAN), (6, AI), (1, HUMAN), (6, AI), (2, HUMAN), (5, AI)]:
        board = board.drop(col, player)
    res = client.post("/api/move", json={"board": board.to_lists(), "column": 3})
    data = res.json()
    assert data["status"] == "human_won"
    assert data["ai_move"] is None


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_all_difficulties_work(difficulty):
    res = client.post("/api/move", json={"board": empty(), "column": 3, "difficulty": difficulty})
    assert res.status_code == 200


def test_rejects_full_column():
    board = Board()
    player = HUMAN
    for _ in range(ROWS):
        board = board.drop(0, player)
        player = AI if player == HUMAN else HUMAN
    res = client.post("/api/move", json={"board": board.to_lists(), "column": 0})
    assert res.status_code == 400
    assert "full" in res.json()["detail"]


def test_rejects_wrong_turn():
    board = Board().drop(0, HUMAN)
    res = client.post("/api/move", json={"board": board.to_lists(), "column": 1})
    assert res.status_code == 400


def test_rejects_invalid_board():
    res = client.post("/api/move", json={"board": [[0] * COLS], "column": 0})
    assert res.status_code == 400


@pytest.mark.parametrize("payload", [
    {"board": [[0] * COLS] * ROWS, "column": COLS},
    {"board": [[0] * COLS] * ROWS, "column": 0, "difficulty": "impossible"},
    {"column": 0},
])
def test_schema_validation(payload):
    assert client.post("/api/move", json=payload).status_code == 422
