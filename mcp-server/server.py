#!/usr/bin/env python3
"""MCP server exposing TaskFlow's own REST API as tools.

Thin HTTP-client wrapper around the running FastAPI backend — not a second
store. The backend (`uv run uvicorn app.main:app --port 8000` from
`backend/`) must already be running; this server has no state of its own.

Usage (stdio transport, for Claude Desktop):
    uv run server.py
"""

import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("taskflow_mcp")

TASKFLOW_API_URL = os.environ.get("TASKFLOW_API_URL", "http://127.0.0.1:8000")


async def _request(method: str, path: str, **kwargs: Any) -> httpx.Response:
    async with httpx.AsyncClient(base_url=TASKFLOW_API_URL, timeout=30.0) as client:
        return await client.request(method, path, **kwargs)


def _handle_api_error(e: Exception) -> str:
    if isinstance(e, httpx.ConnectError):
        return (
            f"Error: Could not reach the TaskFlow backend at {TASKFLOW_API_URL}. "
            "Is `uv run uvicorn app.main:app --port 8000` running in backend/?"
        )
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 404:
            return "Error: Task not found. Check the task_id is correct."
        if e.response.status_code == 422:
            return f"Error: Invalid input — {e.response.text}"
        if e.response.status_code == 502:
            return "Error: Triage service unavailable (the Claude API call failed)."
        return f"Error: TaskFlow API returned status {e.response.status_code}: {e.response.text}"
    if isinstance(e, httpx.TimeoutException):
        return "Error: Request to the TaskFlow backend timed out."
    return f"Error: Unexpected error occurred: {type(e).__name__}: {e}"


class CreateTaskInput(BaseModel):
    title: str = Field(..., description="Task title", min_length=1)
    description: str = Field(default="", description="Optional longer description")
    priority: str = Field(
        default="medium",
        description="Initial priority",
        pattern="^(low|medium|high)$",
    )


class UpdateTaskInput(BaseModel):
    task_id: str = Field(..., description="ID of the task to update")
    title: str | None = Field(default=None, description="New title, if changing it")
    description: str | None = Field(default=None, description="New description, if changing it")
    status: str | None = Field(
        default=None, description="New status", pattern="^(todo|doing|done)$"
    )
    priority: str | None = Field(
        default=None, description="New priority", pattern="^(low|medium|high)$"
    )


@mcp.tool(
    name="taskflow_list_tasks",
    annotations={
        "title": "List TaskFlow Tasks",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def taskflow_list_tasks() -> str:
    """List every task in TaskFlow.

    Returns:
        str: JSON array of Task objects (id, title, description, status,
        priority, created_at, updated_at), or an error string prefixed
        "Error:".

    Examples:
        - Use when: "What tasks do I have?" or "Show me everything in TaskFlow"
        - Don't use when: you already have a task_id and just need that one
          task's details (use taskflow_get_task instead)
    """
    try:
        resp = await _request("GET", "/tasks")
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="taskflow_get_task",
    annotations={
        "title": "Get TaskFlow Task",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def taskflow_get_task(task_id: str) -> str:
    """Get a single task by ID.

    Args:
        task_id: The task's id, as returned by taskflow_list_tasks or
            taskflow_create_task.

    Returns:
        str: JSON Task object, or "Error: Task not found" if the id doesn't exist.
    """
    try:
        resp = await _request("GET", f"/tasks/{task_id}")
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="taskflow_create_task",
    annotations={
        "title": "Create TaskFlow Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def taskflow_create_task(params: CreateTaskInput) -> str:
    """Create a new task in TaskFlow. Starts in "todo" status.

    Args:
        params (CreateTaskInput): title (required), description (optional),
            priority (optional, defaults to "medium").

    Returns:
        str: JSON of the newly created Task (includes its generated id), or
        an error string.

    Examples:
        - Use when: "Add a task to review the PR" -> title="Review the PR"
        - Don't use when: the task already exists and you're changing it
          (use taskflow_update_task instead)
    """
    try:
        resp = await _request("POST", "/tasks", json=params.model_dump())
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="taskflow_update_task",
    annotations={
        "title": "Update TaskFlow Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def taskflow_update_task(params: UpdateTaskInput) -> str:
    """Update an existing task's title, description, status, and/or priority.

    Only the fields you provide are changed — omitted fields keep their
    current value.

    Args:
        params (UpdateTaskInput): task_id (required), plus any of title,
            description, status ("todo"/"doing"/"done"), priority
            ("low"/"medium"/"high").

    Returns:
        str: JSON of the updated Task, or "Error: Task not found".

    Examples:
        - Use when: "Mark task X as done" -> task_id=X, status="done"
        - Don't use when: creating a brand new task (use taskflow_create_task)
    """
    try:
        update_fields = params.model_dump(exclude={"task_id"}, exclude_none=True)
        resp = await _request("PATCH", f"/tasks/{params.task_id}", json=update_fields)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="taskflow_delete_task",
    annotations={
        "title": "Delete TaskFlow Task",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def taskflow_delete_task(task_id: str) -> str:
    """Permanently delete a task. This cannot be undone.

    Args:
        task_id: The id of the task to delete.

    Returns:
        str: "Deleted task <task_id>" on success, or "Error: Task not found".
    """
    try:
        resp = await _request("DELETE", f"/tasks/{task_id}")
        resp.raise_for_status()
        return f"Deleted task {task_id}"
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="taskflow_triage_task",
    annotations={
        "title": "AI-Triage TaskFlow Task",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def taskflow_triage_task(task_id: str) -> str:
    """Ask TaskFlow's AI triage endpoint to suggest a priority for a task.

    Calls the Claude API under the hood (via the backend). Does NOT modify
    the task — it only returns a suggestion with a rationale. Use
    taskflow_update_task separately if you want to apply it.

    Args:
        task_id: The id of the task to triage.

    Returns:
        str: JSON {"priority": "low"|"medium"|"high", "rationale": str}, or
        "Error: Triage service unavailable" if the underlying Claude API
        call failed.
    """
    try:
        resp = await _request("POST", f"/tasks/{task_id}/triage")
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return _handle_api_error(e)


if __name__ == "__main__":
    mcp.run()
