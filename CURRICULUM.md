# Curriculum status

Live tracker for the seven-phase plan. Full rationale, concepts, and
exercises for each phase are in [README.md](README.md) — this file just
tracks progress.

## Status

- [x] 00 — Setup
- [x] 01 — Foundations (CLAUDE.md, plan mode)
- [x] 02 — Agentic workflow (skills, subagents, hooks)
- [ ] 03 — Testing (pytest, Vitest, verify skill)
- [ ] 04 — CI/CD (GitHub Actions, code-review, ultrareview)
- [ ] 05 — Deployment (Docker, secrets, real deploy target)
- [ ] 06 — Observability (structured logging, LLM call tracing)
- [ ] 07 — MCP & agents (own MCP server, Agent SDK, Cowork)

## Phase 00 — Setup

- Repo initialized, git identity configured
- `uv` installed for Python tooling
- `backend/` — FastAPI app scaffold, managed with `uv`
- `frontend/` — Vite + React + TypeScript scaffold

## Phase 01 — Foundations

- `CLAUDE.md` written with real conventions/commands/gotchas for this repo
- Used plan mode to design the `Task` data model and CRUD API before writing
  any code (plan approved, then implemented)
- Backend: `Task`/`TaskCreate`/`TaskUpdate` models, in-memory `TaskStore`,
  `/tasks` CRUD routes, 6 passing tests
- Frontend: task list + add/status-change/delete UI wired to the API,
  verified live in the browser (create → update → delete round trip)

## Phase 02 — Agentic workflow

- `ANTHROPIC_API_KEY` wired via `pydantic-settings`, read from gitignored
  `backend/.env`
- `/new-endpoint` project skill written (`.claude/commands/new-endpoint.md`)
- Milestone: AI-triage endpoint (`POST /tasks/{id}/triage`) scaffolded with
  `/new-endpoint` — Claude tool-use call suggests a priority + rationale
  without mutating the task; 404/502 handled; tests mock the Claude call;
  frontend has a matching wrapper + "Suggest priority" button
- Hook: `PostToolUse` on `Write|Edit` auto-runs `ruff --fix` (backend) or
  `oxlint --fix` (frontend) based on which directory changed
  (`.claude/settings.json`) — verified live: an unused import introduced via
  Edit was auto-removed on the next edit
- Permission allowlist narrowed to the dev loop (pytest/ruff/uvicorn/npm
  scripts, read-only git); commits/pushes/destructive commands still prompt
- Explore subagent exercise: delegated tracing the `priority` field end to
  end across backend/frontend — subagent returned cited file:line findings
  independently

## Phase 03 — Testing (next)

Goal: pytest for the API (already have some coverage — extend it), Vitest +
React Testing Library for the frontend, TDD loop, and the `verify` skill for
end-to-end proof beyond green tests.
