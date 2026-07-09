from fastapi.testclient import TestClient

from app.main import app
from app.models import TaskPriority, TriageSuggestion

client = TestClient(app)


def test_triage_returns_suggestion(monkeypatch) -> None:
    created = client.post("/tasks", json={"title": "Fix prod outage"}).json()

    def fake_suggest_priority(task):
        return TriageSuggestion(priority=TaskPriority.high, rationale="Outages are urgent.")

    monkeypatch.setattr("app.main.suggest_priority", fake_suggest_priority)

    response = client.post(f"/tasks/{created['id']}/triage")
    assert response.status_code == 200
    body = response.json()
    assert body["priority"] == "high"
    assert body["rationale"] == "Outages are urgent."


def test_triage_unknown_task_returns_404() -> None:
    assert client.post("/tasks/does-not-exist/triage").status_code == 404


def test_triage_upstream_failure_returns_502(monkeypatch) -> None:
    created = client.post("/tasks", json={"title": "Anything"}).json()

    def failing_suggest_priority(task):
        raise RuntimeError("Claude API unavailable")

    monkeypatch.setattr("app.main.suggest_priority", failing_suggest_priority)

    response = client.post(f"/tasks/{created['id']}/triage")
    assert response.status_code == 502
