# taskflow-mcp

A small MCP server exposing TaskFlow's own REST API as tools, so you can
manage tasks by chatting with Claude Desktop instead of using the app's UI.

It's a thin `httpx` wrapper — no state of its own. Every tool call is a
real HTTP request to the running backend.

## Precondition

The backend must be running first:

```bash
cd ../backend
uv run uvicorn app.main:app --port 8000
```

## Try it standalone

```bash
uv run mcp dev server.py
```

Opens the MCP Inspector so you can call each tool directly before wiring
up Claude Desktop.

## Connect to Claude Desktop

Add this to Claude Desktop's config
(`~/Library/Application Support/Claude/claude_desktop_config.json` on
macOS), swapping in the absolute path to this repo:

```json
{
  "mcpServers": {
    "taskflow": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/ClaudePro/mcp-server", "server.py"]
    }
  }
}
```

Restart Claude Desktop. You should be able to ask it things like "list my
TaskFlow tasks" or "create a task to review the PR" and see it call the
tools below.

## Tools

| Tool | What it does |
|---|---|
| `taskflow_list_tasks` | List every task |
| `taskflow_get_task` | Get one task by id |
| `taskflow_create_task` | Create a task (title, description, priority) |
| `taskflow_update_task` | Update a task's title/description/status/priority |
| `taskflow_delete_task` | Delete a task (irreversible) |
| `taskflow_triage_task` | Ask the AI triage endpoint for a priority suggestion (doesn't apply it) |

By default it talks to `http://127.0.0.1:8000` — override with the
`TASKFLOW_API_URL` env var if the backend is running elsewhere.
