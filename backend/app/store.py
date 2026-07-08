from datetime import UTC, datetime
from uuid import uuid4

from app.models import Task, TaskCreate, TaskStatus, TaskUpdate


class TaskStore:
    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def list(self) -> list[Task]:
        return list(self._tasks.values())

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def create(self, data: TaskCreate) -> Task:
        now = datetime.now(UTC)
        task = Task(
            id=uuid4().hex,
            title=data.title,
            description=data.description,
            status=TaskStatus.todo,
            priority=data.priority,
            created_at=now,
            updated_at=now,
        )
        self._tasks[task.id] = task
        return task

    def update(self, task_id: str, data: TaskUpdate) -> Task | None:
        existing = self._tasks.get(task_id)
        if existing is None:
            return None
        updated = existing.model_copy(
            update={
                **data.model_dump(exclude_unset=True),
                "updated_at": datetime.now(UTC),
            }
        )
        self._tasks[task_id] = updated
        return updated

    def delete(self, task_id: str) -> bool:
        return self._tasks.pop(task_id, None) is not None


# Single in-process instance; won't survive a restart — fine for Phase 01.
store = TaskStore()
