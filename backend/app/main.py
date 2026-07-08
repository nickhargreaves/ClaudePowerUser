from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import Task, TaskCreate, TaskUpdate
from app.store import store

app = FastAPI(title="TaskFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks() -> list[Task]:
    return store.list()


@app.post("/tasks", status_code=201)
def create_task(data: TaskCreate) -> Task:
    return store.create(data)


@app.get("/tasks/{task_id}")
def get_task(task_id: str) -> Task:
    task = store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/tasks/{task_id}")
def update_task(task_id: str, data: TaskUpdate) -> Task:
    task = store.update(task_id, data)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str) -> None:
    if not store.delete(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
