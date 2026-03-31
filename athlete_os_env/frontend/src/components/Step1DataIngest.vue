<template>
  <div class="card">
    <h2 class="text-xl font-semibold mb-4">Step 1 — Data Ingest</h2>
    <p class="text-gray-400 text-sm mb-6">
      Upload player stats, select a sport/league, or use built-in sample data to seed the simulation.
    </p>

    <div class="grid md:grid-cols-2 gap-6 mb-6">
      <div>
        <label class="block text-sm font-medium text-gray-400 mb-2">Sport / League</label>
        <select v-model="league" class="w-full bg-surface-700 border border-surface-600 rounded-lg px-4 py-2.5 text-gray-200 focus:outline-none focus:border-accent-cyan">
          <option value="premier_league">Premier League (Soccer)</option>
          <option value="la_liga">La Liga (Soccer)</option>
          <option value="nba">NBA (Basketball)</option>
          <option value="ipl">IPL (Cricket)</option>
          <option value="nfl">NFL (American Football)</option>
        </select>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-400 mb-2">Data Source</label>
        <select v-model="dataSource" class="w-full bg-surface-700 border border-surface-600 rounded-lg px-4 py-2.5 text-gray-200 focus:outline-none focus:border-accent-cyan">
          <option value="sample">Built-in Sample Players</option>
          <option value="upload">Upload CSV/JSON</option>
          <option value="api">ESPN / SportsRadar API</option>
        </select>
      </div>
    </div>

    <div v-if="dataSource === 'upload'" class="mb-6">
      <div
        class="border-2 border-dashed border-surface-600 rounded-lg p-10 text-center hover:border-accent-cyan/50 transition-colors cursor-pointer"
        @dragover.prevent
        @drop.prevent="handleDrop"
      >
        <p class="text-gray-400">Drop your CSV or JSON file here</p>
      </div>
    </div>

    <div v-if="dataSource === 'sample'" class="mb-6">
      <p class="text-sm text-accent-emerald">Using built-in sample data ({{ playerCount }} players available)</p>
    </div>

    <div class="flex justify-end">
      <button class="btn-primary" @click="$emit('next')">
        Continue to Persona Forge
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useSquadStore } from '../store/squad.js'

const emit = defineEmits(['next'])
const squadStore = useSquadStore()

const league = ref('premier_league')
const dataSource = ref('sample')
const playerCount = ref(squadStore.players.length || 7)

function handleDrop(e) {
  const file = e.dataTransfer.files[0]
  if (file) console.log('Uploaded:', file.name)
}
</script>
