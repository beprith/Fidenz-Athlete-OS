<template>
  <div class="flex items-center gap-3 text-xs">
    <div v-for="agent in agents" :key="agent.id" class="flex items-center gap-1.5" :title="agent.label">
      <span class="pulse-dot" :style="{ background: statusColor(agent.status) }"></span>
      <span class="text-gray-400 hidden sm:inline">{{ agent.label }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useSimulationStore } from '../store/simulation.js'

const simStore = useSimulationStore()

const agentList = [
  { id: 'ontology', label: 'Ontology' },
  { id: 'graph', label: 'Graph' },
  { id: 'persona', label: 'Persona' },
  { id: 'sim', label: 'Sim' },
  { id: 'grader', label: 'Grader' },
]

const agents = computed(() =>
  agentList.map((a) => ({
    ...a,
    status: simStore.agentStatuses[a.id] || 'idle',
  }))
)

function statusColor(status) {
  const m = {
    idle: '#6b7280',
    building: '#f59e0b',
    running: '#06b6d4',
    simulating: '#06b6d4',
    grading: '#8b5cf6',
    done: '#10b981',
    error: '#f43f5e',
  }
  return m[status] || '#6b7280'
}
</script>
