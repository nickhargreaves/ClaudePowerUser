---
description: Scaffold a new FastAPI route with its models, test, and matching frontend wrapper
---

Scaffold a new backend route for TaskFlow. If what the route does, its HTTP
method, or its path isn't clear from the request, ask before writing code.

Always create these together, in the same change — never skip the test:

1. **Models** — Pydantic request/response models in `backend/app/models.py`,
   or reuse existing ones if they already fit. Follow the `Task`/`TaskCreate`/
   `TaskUpdate` pattern already in that file (separate input vs. output shapes
   where the server sets fields like `id` or timestamps).
2. **Route handler** — added to `backend/app/main.py`, following the
   thin-handler convention from `CLAUDE.md`: the handler itself should just
   parse input, call into a plain function/store, and return — push any real
   logic into `app/` modules so it's testable without spinning up the app.
3. **Test** — in `backend/tests/`, using the existing `TestClient` pattern
   (see `test_health.py`, `test_tasks.py`). Cover at least the happy path and
   one failure case (404 for a missing resource, or a validation error for
   bad input) — whichever applies to this route.

Then check whether the frontend needs a matching wrapper: if this route is
something the UI would call, add a typed function to `frontend/src/api.ts`
(and update `frontend/src/types.ts` if the shape is new), following the
existing `listTasks`/`createTask`/etc. pattern. Skip this if the route is
backend-internal only.

Run `uv run pytest -q` and `uv run ruff check .` in `backend/` before
considering the work done — don't hand back a route you haven't proven
passes its own test.

Once everything passes, stop and ask the user if they're ready to commit the
changes. Do not commit automatically.
