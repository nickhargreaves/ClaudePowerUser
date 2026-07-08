# TaskFlow — Claude Mastery Curriculum

A small AI-augmented task &amp; project tracker — Python (FastAPI) backend,
TypeScript (React + Vite) frontend — built as the running project for a
seven-phase curriculum in using Claude Code, Claude Desktop, and Cowork at an
expert level: coding, agentic workflows, testing, CI/CD, deployment, and
observability.

For live status (what's done, what's next), see [CURRICULUM.md](CURRICULUM.md).

## The project

TaskFlow uses the Claude API itself — to triage new tasks, summarize stale
threads, and suggest next actions — which gives the curriculum a real reason
to touch every part of the lifecycle: an API to test, a UI to ship, an LLM
call to observe, and a deploy target to watch in production.

**Stack:** FastAPI &middot; React + Vite + TypeScript &middot; pytest / vitest
&middot; GitHub Actions &middot; Docker &middot; Claude Agent SDK

## The seven phases

### 00 — Setup

Get the repo, the CLI, and terminal habits in order before any lesson, so
later phases aren't fighting the environment.

- `git init`, first commit
- Scaffold `backend/` (FastAPI + uv) and `frontend/` (Vite + React + TS)
- Install/update the Claude Code CLI, sign in

**Why it matters:** Claude Code reasons about the repo it's sitting in. A
clean, committed baseline means every later diff is legible — to you and to
Claude.

### 01 — Foundations: talking to Claude Code well

The highest-leverage skill is giving Claude the right context before it
writes a line. This phase is about the habits that separate "prompt and pray"
from deliberate collaboration.

**Concepts**
- Writing a real `CLAUDE.md` (conventions, commands, gotchas)
- Plan mode vs. auto-accept — when to demand a plan first
- Scoping asks: small diffs vs. "build the whole feature"
- Reading and steering the diff, not just approving it

**Exercises**
- Draft `CLAUDE.md` for TaskFlow by hand, then ask Claude to critique it
- Use plan mode to design the data model before any code exists
- Have Claude scaffold the FastAPI skeleton + Vite app from that plan

**Milestone:** TaskFlow has a running FastAPI backend (health check + task
CRUD stub) and a React shell that lists tasks from it, plus a `CLAUDE.md` you'd
hand to a new teammate.

### 02 — The agentic workflow: skills, subagents, hooks

This is where Claude Code stops being "a chatbot with file access" and becomes
a configurable system you shape to your project.

**Concepts**
- Custom slash-command skills vs. built-in ones
- When to delegate to a subagent (Explore, Plan) vs. do it inline
- Hooks: enforcing lint/format on every edit automatically
- Permission modes and why narrow allowlists beat blanket trust

**Exercises**
- Write a project skill, e.g. `/new-endpoint` that scaffolds a FastAPI route +
  Pydantic model + test stub together
- Add a post-edit hook that runs `ruff` and `eslint --fix`
- Use an Explore subagent to answer "where does auth happen?" once the
  codebase has enough surface area to make that non-trivial

**Milestone:** the "AI triage" endpoint exists — a route that calls the
Claude API to classify an incoming task's priority, built using your own
`/new-endpoint` skill.

### 03 — Testing: making Claude prove it, not just claim it

Claude will tell you something works. This phase is about never taking that
on faith — for both regular code and the LLM-touching code, which fails
differently.

**Concepts**
- pytest for the API, Vitest + React Testing Library for the UI
- TDD with Claude: write the failing test first, then ask it to make it pass
- Testing LLM-backed endpoints: mock the Claude client, assert on
  prompts/shape, not exact wording
- The `verify` skill — driving the real flow end-to-end, not just green tests

**Exercises**
- Backfill tests for Phase 1–2 endpoints and components
- Write a test that asserts the triage endpoint degrades gracefully if the
  Claude API errors
- Run `/verify` after a real feature change and compare it to "tests passed"
  alone

**Milestone:** backend and frontend both have a real test suite, including
one test that deliberately breaks the Claude call to check the fallback path.

### 04 — CI/CD: Claude as reviewer, not just author

Writing code is half the job. This phase wires Claude into the gate that
decides whether code merges — a genuinely different skill from writing it.

**Concepts**
- GitHub Actions: lint, typecheck, test on every PR
- `/code-review` at low/medium effort for routine PRs
- Ultrareview for the PR that matters — multi-agent cloud review before merge
- Branch protection + required checks so the pipeline isn't advisory

**Exercises**
- Add a `.github/workflows/ci.yml` covering both backend and frontend
- Open a real PR for a TaskFlow feature and run `/code-review` on it before
  merging
- Deliberately introduce one subtle bug, see whether review catches it

**Milestone:** no PR reaches `main` without CI green and a Claude review pass
— verified by watching one actually get blocked.

### 05 — Deployment: from laptop to a real URL

Best practice here is less about Claude-specific tricks and more about having
Claude execute deployment discipline you'd want from any engineer:
reproducible builds, secrets handled correctly, no surprise prod pushes.

**Concepts**
- Dockerizing the FastAPI service; static build for the TS frontend
- Secrets management (Claude API key never in the repo or the image)
- A real target: Fly.io / Render / a VPS — pick one and commit
- Why Claude should propose the deploy plan and you should approve each risky
  step

**Exercises**
- Write the Dockerfile and a minimal docker-compose for local parity with prod
- Wire CD: merge to main → build → deploy, gated on CI passing
- Do one deploy live and watch Claude narrate risk before each
  destructive-adjacent step

**Milestone:** TaskFlow is live at a real URL, deployed by a pipeline, with
the Claude API key injected as a secret, never committed.

### 06 — Observability: watching an LLM-backed system in the wild

Traditional observability plus one new problem: LLM calls fail silently,
drift in latency, and cost real money per request. This phase is about
seeing that.

**Concepts**
- Structured logging (request id, latency, status) on every route
- Tracing the triage call specifically: prompt version, tokens, latency, cost
- Alerting on Claude API error rate / latency spikes, not just HTTP 500s
- Using Claude Code itself to read logs and root-cause a production incident

**Exercises**
- Add structured logging + a minimal dashboard (even just log-based)
- Instrument the triage endpoint with token/cost/latency metrics
- Simulate an incident (bad prompt, timeout) and use Claude Code to diagnose
  it from logs alone

**Milestone:** a dashboard shows triage-call latency and cost over time, and
you've used Claude to debug one deliberately-injected incident from logs
alone.

### 07 — Going further: MCP servers and multi-agent design

The capstone: build the kind of tool you've been using all along, and use
orchestration patterns beyond single-agent chat.

**Concepts**
- Building a small MCP server (e.g. exposing TaskFlow's own API as tools)
- Claude Agent SDK basics — a custom agent instead of raw API calls
- Multi-agent orchestration: when parallel subagents actually pay off vs. add
  noise
- Where Claude Desktop and Cowork fit vs. Claude Code — same model, different
  loop

**Exercises**
- Write an MCP server wrapping TaskFlow, connect it in Claude Desktop, manage
  tasks by chatting
- Rebuild the triage feature on the Agent SDK instead of a raw API call
- Retire one manual chore (e.g. weekly stale-task summary) to Cowork or a
  scheduled agent

**Milestone:** you can manage TaskFlow tasks from Claude Desktop via your own
MCP server, and a scheduled agent sends a weekly summary without you asking.

## Pace

| Phase | Claude surface | Time (evenings) |
|---|---|---|
| 00 Setup | CLI install, repo init | 1 |
| 01 Foundations | CLAUDE.md, plan mode | 2–3 |
| 02 Agentic workflow | Skills, subagents, hooks | 2–3 |
| 03 Testing | verify skill, TDD loop | 2 |
| 04 CI/CD | /code-review, ultrareview | 2 |
| 05 Deployment | Guided deploy, risk narration | 2 |
| 06 Observability | Log-driven debugging | 2–3 |
| 07 MCP & agents | MCP server, Agent SDK, Cowork | 3–4 |

Suggested pace: one phase every 3–5 days, evenings only — roughly 6–8 weeks
end to end. Each phase's milestone is the gate: don't start the next phase
until TaskFlow actually does the thing, not just "the code looks right."

## Running it locally

```bash
# backend
cd backend && uv run uvicorn app.main:app --reload --port 8000

# frontend (separate shell)
cd frontend && npm run dev
```

The frontend dev server proxies `/api/*` to `http://127.0.0.1:8000`.
