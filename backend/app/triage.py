import anthropic

from app.config import settings
from app.models import Task, TaskPriority, TriageSuggestion

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

_TRIAGE_TOOL = {
    "name": "suggest_priority",
    "description": "Suggest a priority level for a task with a short rationale.",
    "input_schema": {
        "type": "object",
        "properties": {
            "priority": {"type": "string", "enum": ["low", "medium", "high"]},
            "rationale": {
                "type": "string",
                "description": "One sentence explaining the suggestion.",
            },
        },
        "required": ["priority", "rationale"],
    },
}


def suggest_priority(task: Task) -> TriageSuggestion:
    message = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        tools=[_TRIAGE_TOOL],
        tool_choice={"type": "tool", "name": "suggest_priority"},
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
    for block in message.content:
        if block.type == "tool_use" and block.name == "suggest_priority":
            return TriageSuggestion(
                priority=TaskPriority(block.input["priority"]),
                rationale=block.input["rationale"],
            )
    raise RuntimeError("Claude did not return a triage suggestion")
