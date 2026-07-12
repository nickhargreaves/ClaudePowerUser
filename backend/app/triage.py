import time

import anthropic
from anthropic import beta_tool

from app.config import settings
from app.logging_config import log_event
from app.models import Task, TaskPriority, TriageSuggestion

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

# Verify against https://www.anthropic.com/pricing before trusting
# estimated_cost_usd for real budgeting — these are illustrative constants,
# not pulled from a live pricing source, and will go stale.
_INPUT_COST_PER_MTOK = 1.00
_OUTPUT_COST_PER_MTOK = 5.00


def suggest_priority(task: Task) -> TriageSuggestion:
    start = time.perf_counter()
    captured: dict[str, str] = {}

    @beta_tool
    def suggest_priority_tool(priority: str, rationale: str) -> str:
        """Record the suggested priority and rationale for this task.

        Args:
            priority: One of "low", "medium", "high".
            rationale: One sentence explaining the suggestion.
        """
        captured["priority"] = priority
        captured["rationale"] = rationale
        return "recorded"

    try:
        runner = _client.beta.messages.tool_runner(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            tools=[suggest_priority_tool],
            tool_choice={"type": "tool", "name": "suggest_priority_tool"},
            # Forcing tool_choice means Claude would be forced to call this
            # same tool again on any follow-up turn too — cap the loop at
            # one round trip rather than let it force-loop until the SDK's
            # own iteration ceiling.
            max_iterations=1,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Suggest a priority for this task.\n\n"
                        f"Title: {task.title}\n"
                        f"Description: {task.description or '(none)'}"
                    ),
                }
            ],
        )
        # We only need suggest_priority_tool to have been called once
        # (guaranteed by the forced tool_choice) — the runner executes it
        # as a side effect of advancing the loop, regardless of whether it
        # goes on to make a second round trip for a final text response.
        # Track the last message we saw purely for its usage stats.
        last_message = None
        for message in runner:
            last_message = message
    except Exception:
        _log_triage_call(task, start, status="error")
        raise

    if "priority" not in captured:
        _log_triage_call(task, start, status="error")
        raise RuntimeError("Claude did not return a triage suggestion")

    try:
        suggestion = TriageSuggestion(
            priority=TaskPriority(captured["priority"]),
            rationale=captured["rationale"],
        )
    except (KeyError, ValueError):
        # Model returned a tool call that doesn't match our schema (e.g. a
        # priority outside the enum) — log it as the failure it is, not as
        # a successful call.
        _log_triage_call(task, start, status="error")
        raise

    usage = last_message.usage if last_message is not None else None
    _log_triage_call(
        task,
        start,
        status="ok",
        priority=suggestion.priority.value,
        input_tokens=usage.input_tokens if usage else 0,
        output_tokens=usage.output_tokens if usage else 0,
    )
    return suggestion


def _log_triage_call(
    task: Task,
    start: float,
    *,
    status: str,
    priority: str | None = None,
    input_tokens: int = 0,
    output_tokens: int = 0,
) -> None:
    estimated_cost_usd = round(
        (input_tokens * _INPUT_COST_PER_MTOK + output_tokens * _OUTPUT_COST_PER_MTOK) / 1_000_000,
        6,
    )
    log_event(
        "triage_call",
        task_id=task.id,
        status=status,
        priority=priority,
        latency_ms=round((time.perf_counter() - start) * 1000, 2),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost_usd=estimated_cost_usd,
    )
