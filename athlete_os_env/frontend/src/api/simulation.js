import api from './index.js'

export async function getTasks() {
  const { data } = await api.get('/api/tasks')
  return data.tasks
}

export async function getPlayers() {
  const { data } = await api.get('/api/players')
  return data.players
}

export async function getTeams() {
  const { data } = await api.get('/api/teams')
  return data.teams
}

export async function getGraph() {
  const { data } = await api.get('/api/graph')
  return data
}

export async function getReport() {
  const { data } = await api.get('/api/report')
  return data
}

export async function uploadData(file) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post('/api/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
