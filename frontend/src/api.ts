import type { Task, TaskPriority, TriageSuggestion } from './types'

const BASE = '/api/tasks'

export async function listTasks(): Promise<Task[]> {
  const res = await fetch(BASE)
  if (!res.ok) throw new Error(`Failed to list tasks: ${res.status}`)
  return res.json()
}

export async function createTask(title: string, priority: TaskPriority = 'medium'): Promise<Task> {
  const res = await fetch(BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, priority }),
  })
  if (!res.ok) throw new Error(`Failed to create task: ${res.status}`)
  return res.json()
}

export async function updateTask(id: string, patch: Partial<Pick<Task, 'title' | 'description' | 'status' | 'priority'>>): Promise<Task> {
  const res = await fetch(`${BASE}/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(patch),
  })
  if (!res.ok) throw new Error(`Failed to update task: ${res.status}`)
  return res.json()
}

export async function deleteTask(id: string): Promise<void> {
  const res = await fetch(`${BASE}/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`Failed to delete task: ${res.status}`)
}

export async function triageTask(id: string): Promise<TriageSuggestion> {
  const res = await fetch(`${BASE}/${id}/triage`, { method: 'POST' })
  if (!res.ok) throw new Error(`Failed to triage task: ${res.status}`)
  return res.json()
}
