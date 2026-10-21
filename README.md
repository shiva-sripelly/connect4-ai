# Connect Four AI

[![CI](https://github.com/YOUR-USERNAME/connect4-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR-USERNAME/connect4-ai/actions/workflows/ci.yml)

Play Connect Four against an AI that uses **negamax search with alpha-beta pruning**. The project includes a pure-Python game engine, a FastAPI backend, a browser UI, and a terminal mode, all covered by an automated test suite that runs in CI.

## Features

- **Game engine:** immutable board with full validation. It rejects impossible positions, such as floating pieces or wrong piece counts.
- **AI:** negamax with alpha-beta pruning, center-first move ordering, and a window-based heuristic. It prefers faster wins and delays losses.
- **Three difficulty levels:** easy (search depth 1), medium (depth 3), and hard (depth 6). A hard move takes well under a second.
- **Stateless REST API:** the client sends the whole board, and the server validates it, plays the human's move, and replies with the AI's move.
- **Web UI:** a single HTML page with no build step and no frontend dependencies.
- **CLI:** play in the terminal with `python -m connect4`.
- **Quality:** type hints, 44 pytest tests, ruff linting, GitHub Actions CI on Python 3.10 to 3.12, and a Dockerfile.

## Project Structure

```
connect4-ai/
├── connect4/
│   ├── engine.py        # Board, rules, win detection, validation
│   ├── ai.py            # Negamax + alpha-beta search and heuristic
│   ├── api.py           # FastAPI app (/api/move, /api/health, /)
│   ├── cli.py           # Terminal game
│   └── static/index.html
├── tests/
│   ├── test_engine.py   # Rules, validation, win/draw detection
│   ├── test_ai.py       # Tactics (win/block), determinism, strength vs random
│   └── test_api.py      # Endpoints, error handling, schema validation
├── .github/workflows/ci.yml
├── Dockerfile
└── pyproject.toml
```

The engine has no dependencies. The AI depends only on the engine, and the API and CLI are thin layers on top. This separation lets each layer be tested in isolation.

## Quick Start

Requires Python 3.10 or later.

```bash
git clone https://github.com/YOUR-USERNAME/connect4-ai.git
cd connect4-ai
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

**Play in the browser:**

```bash
uvicorn connect4.api:app --reload
```

Then open http://localhost:8000. Interactive API docs are available at http://localhost:8000/docs.

**Play in the terminal:**

```bash
python -m connect4 --difficulty hard
```

**Run with Docker:**

```bash
docker build -t connect4-ai .
docker run -p 8000:8000 connect4-ai
```

## Testing

```bash
pytest -v        # 44 tests
ruff check .     # lint
```

What the tests verify:

| Area | Checks |
|------|--------|
| Engine | Piece placement and stacking, immutability, full-column and out-of-range errors, horizontal, vertical and diagonal wins, draws, and rejection of impossible boards |
| AI | Takes an immediate win, blocks an immediate loss, opens in the center, never picks a full column, is deterministic, and wins every game against a random player |
| API | Health check, the human move followed by the AI reply, win reporting with the winning line, wrong-turn and full-column errors, and request schema validation (422) |

## API

### `POST /api/move`

Request:

```json
{
  "board": [[0,0,0,0,0,0,0], [0,0,0,0,0,0,0], [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0], [0,0,0,0,0,0,0], [0,0,0,0,0,0,0]],
  "column": 2,
  "difficulty": "hard"
}
```

- `board` is a 6×7 grid. `0` means empty, `1` is the human, and `2` is the AI. Row 0 is the top row.
- `difficulty` is `easy`, `medium`, or `hard`. The default is `hard`.

Response:

```json
{
  "board": [[...], ...],
  "human_move": 2,
  "ai_move": 3,
  "status": "in_progress",
  "winning_line": null
}
```

- `status` is `in_progress`, `human_won`, `ai_won`, or `draw`.
- `winning_line` lists the `[row, col]` cells of the four-in-a-row, or `null`.

Errors:

- `400` for an illegal position, a full column, a game that is already over, or a request sent when it's not the human's turn.
- `422` for a request that doesn't match the schema.

### `GET /api/health`

Returns `{"status": "ok"}`.

## How the AI Works

1. **Negamax** is a compact form of minimax. It uses the fact that a position's score for one player is the negative of its score for the other player.
2. **Alpha-beta pruning** skips branches that cannot change the result. Searching center columns first makes the pruning much more effective.
3. **Terminal scoring:** a win scores `1,000,000 - ply`, so the AI picks the fastest win and the slowest loss.
4. **Heuristic:** at the depth limit, the AI scores every line of four cells. Three of its own pieces with an open cell scores +5, two with two open cells scores +2, and an opponent's three with an open cell scores -4. Pieces in the center column add a bonus.

## License

MIT
"# connect4-ai" 
