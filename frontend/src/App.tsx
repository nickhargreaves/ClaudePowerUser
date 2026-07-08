import { useEffect, useState } from 'react'
import './App.css'
import { createTask, deleteTask, listTasks, updateTask } from './api'
import type { Task, TaskStatus } from './types'

type HealthStatus = 'checking' | 'ok' | 'unreachable'

function App() {
  const [health, setHealth] = useState<HealthStatus>('checking')
  const [tasks, setTasks] = useState<Task[]>([])
  const [title, setTitle] = useState('')

  useEffect(() => {
    fetch('/api/health')
      .then((res) => (res.ok ? res.json() : Promise.reject(res.status)))
      .then((data: { status: string }) => setHealth(data.status === 'ok' ? 'ok' : 'unreachable'))
      .catch(() => setHealth('unreachable'))

    refreshTasks()
  }, [])

  function refreshTasks() {
    listTasks().then(setTasks).catch(() => setTasks([]))
  }

  async function handleAddTask(event: React.FormEvent) {
    event.preventDefault()
    if (!title.trim()) return
    await createTask(title.trim())
    setTitle('')
    refreshTasks()
  }

  async function handleStatusChange(task: Task, status: TaskStatus) {
    await updateTask(task.id, { status })
    refreshTasks()
  }

  async function handleDelete(task: Task) {
    await deleteTask(task.id)
    refreshTasks()
  }

  return (
    <main className="shell">
      <h1>TaskFlow</h1>
      <p>
        Backend status: <strong className={`status status-${health}`}>{health}</strong>
      </p>

      <form onSubmit={handleAddTask} className="add-task">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="New task title"
        />
        <button type="submit">Add</button>
      </form>

      <ul className="task-list">
        {tasks.map((task) => (
          <li key={task.id} className="task-row">
            <span className="task-title">{task.title}</span>
            <span className="task-priority">{task.priority}</span>
            <select
              value={task.status}
              onChange={(e) => handleStatusChange(task, e.target.value as TaskStatus)}
            >
              <option value="todo">todo</option>
              <option value="doing">doing</option>
              <option value="done">done</option>
            </select>
            <button type="button" onClick={() => handleDelete(task)}>
              Delete
            </button>
          </li>
        ))}
        {tasks.length === 0 && <li className="task-empty">No tasks yet.</li>}
      </ul>
    </main>
  )
}

export default App
