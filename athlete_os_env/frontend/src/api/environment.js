import api from './index.js'

export async function resetEnv(taskId = null) {
  if (taskId) {
    await api.post('/api/set-task', { task_id: taskId })
  }
  const { data } = await api.post('/reset', {})
  return data
}

export async function stepEnv(action) {
  // OpenEnv expects action wrapped: {"action": {...}}
  const { data } = await api.post('/step', { action })
  return data
}

export async function getState() {
  const { data } = await api.get('/state')
  return data
}

export async function getHealth() {
  const { data } = await api.get('/health')
  return data
}
