import { ref, onMounted, onUnmounted } from 'vue'
import { useEpisodeStore } from '../store/episode.js'
import { useSimulationStore } from '../store/simulation.js'

export function useSimSocket() {
  const connected = ref(false)
  const error = ref(null)
  let ws = null
  let reconnectTimer = null

  function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const url = `${protocol}//${host}/ws/live`

    try {
      ws = new WebSocket(url)
    } catch (e) {
      error.value = e.message
      scheduleReconnect()
      return
    }

    ws.onopen = () => {
      connected.value = true
      error.value = null
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleEvent(data)
      } catch (e) {
        /* ignore parse errors */
      }
    }

    ws.onclose = () => {
      connected.value = false
      scheduleReconnect()
    }

    ws.onerror = (e) => {
      error.value = 'WebSocket error'
      connected.value = false
    }
  }

  function handleEvent(data) {
    const episodeStore = useEpisodeStore()
    const simStore = useSimulationStore()

    episodeStore.updateFromWs(data)
    simStore.handleWsEvent(data)
  }

  function scheduleReconnect() {
    if (reconnectTimer) clearTimeout(reconnectTimer)
    reconnectTimer = setTimeout(() => {
      connect()
    }, 3000)
  }

  function disconnect() {
    if (ws) {
      ws.close()
      ws = null
    }
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    connected.value = false
  }

  function send(data) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data))
    }
  }

  onMounted(connect)
  onUnmounted(disconnect)

  return { connected, error, send, disconnect }
}
