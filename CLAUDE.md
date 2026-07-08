# TaskFlow

AI-augmented task tracker. FastAPI backend, React/Vite/TypeScript frontend.
Built as the running project for the Claude mastery curriculum — see
[README.md](README.md) for the full plan and [CURRICULUM.md](CURRICULUM.md)
for live phase status.

## Layout

- `backend/` — FastAPI app, package is `app/`, managed with `uv`
- `frontend/` — Vite + React + TypeScript, dev server proxies `/api/*` to the
  backend on `:8000` (see `vite.config.ts`)
- `.claude/launch.json` — preview server definitions for `backend` and
  `frontend`

## Commands

Backend (run from `backend/`, or prefix with `cd backend &&`):

```bash
uv run uvicorn app.main:app --reload --port 8000   # dev server
uv run pytest -q                                    # tests
uv run ruff check .                                 # lint
```

Frontend (run from `frontend/`):

```bash
npm run dev       # dev server, :5173
npm run build      # tsc -b && vite build
npm run lint        # oxlint (not eslint)
```

`uv` is installed to `~/.local/bin`. If it's not on `PATH` in a fresh shell,
run `source $HOME/.local/bin/env` first.

## Conventions

- Backend: Python 3.11+, type hints everywhere, Pydantic models for
  request/response shapes. Keep route handlers thin — push logic into
  plain functions/modules under `app/` so they're testable without spinning
  up the app.
- Frontend: function components + hooks, no class components. TypeScript
  strict mode is on (`tsconfig.app.json`) — don't silence errors with `any`.
- Tests live next to what they cover: `backend/tests/` mirrors `backend/app/`;
  frontend component tests (once added in Phase 03) sit beside their
  component.
- Every new backend route needs a test in the same PR/commit — don't defer it.
- The Claude API key belongs in `backend/.env` (gitignored), never
  hardcoded, never logged. `pydantic-settings` reads it — see
  `app/main.py` for the pattern once Phase 02 adds the triage endpoint.

## Gotchas

- `pytest` needs `pythonpath = ["."]` (already set in `backend/pyproject.toml`)
  because `app/` isn't installed as a package — imports like
  `from app.main import app` only resolve with that in place.
- The frontend fetches `/api/health`, not `http://localhost:8000/health`
  directly — the Vite proxy strips the `/api` prefix. Keep frontend calls
  going through `/api/*` so dev and prod (once there's a reverse proxy) behave
  the same way.
- Two dev servers, two terminals (or use `.claude/launch.json` via the
  preview tool) — the frontend alone will show "unreachable" if the backend
  isn't also running.
