<template>
  <div class="max-w-7xl mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold mb-6">Squad Chemistry Board</h1>

    <!-- Sport Filter -->
    <div class="flex gap-2 mb-6">
      <button
        v-for="s in sports"
        :key="s.id"
        class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
        :class="activeSport === s.id
          ? 'bg-accent-cyan/20 text-accent-cyan border border-accent-cyan/40'
          : 'bg-surface-700 text-gray-400 border border-surface-600 hover:border-surface-500'"
        @click="activeSport = s.id"
      >
        {{ s.icon }} {{ s.label }}
        <span class="ml-1 text-xs text-gray-500">({{ sportPlayerCount(s.id) }})</span>
      </button>
    </div>

    <div class="grid lg:grid-cols-2 gap-6 mb-8">
      <!-- Field View -->
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">
          {{ activeSport === 'basketball' ? 'Court View' : activeSport === 'cricket' ? 'Field View' : 'Formation View' }}
        </h2>
        <PitchView :players="selectedPlayerObjects" :sport="activeSport" />
      </div>

      <!-- Chemistry Matrix -->
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Chemistry Heatmap</h2>
        <ChemistryMatrix
          v-if="squadStore.chemistryMatrix.length"
          :matrix="squadStore.chemistryMatrix"
          :players="selectedPlayerObjects"
        />
        <p v-else class="text-gray-500 text-sm">Select players and run simulation to see chemistry.</p>
      </div>
    </div>

    <!-- Player Cards -->
    <div class="mb-6">
      <h2 class="text-lg font-semibold mb-4">
        {{ sportLabel }} Players
        <span class="text-sm font-normal text-gray-500">({{ filteredPlayers.length }})</span>
      </h2>
      <div class="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <PlayerCard
          v-for="player in filteredPlayers"
          :key="player.player_id"
          :player="player"
          :selected="squadStore.selectedPlayers.includes(player.player_id)"
          @click="squadStore.togglePlayer(player.player_id)"
        />
      </div>
    </div>

    <!-- Extremes -->
    <div v-if="squadStore.weakestLink || squadStore.strongestPair" class="card">
      <div class="flex gap-8">
        <div v-if="squadStore.strongestPair">
          <span class="text-accent-emerald font-semibold">Strongest Pair:</span>
          <span class="text-gray-300 ml-2">{{ squadStore.strongestPair.players.join(' ↔ ') }} ({{ squadStore.strongestPair.score.toFixed(2) }})</span>
        </div>
        <div v-if="squadStore.weakestLink">
          <span class="text-accent-rose font-semibold">Weakest Link:</span>
          <span class="text-gray-300 ml-2">{{ squadStore.weakestLink.players.join(' ↔ ') }} ({{ squadStore.weakestLink.score.toFixed(2) }})</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSquadStore } from '../store/squad.js'
import PlayerCard from '../components/PlayerCard.vue'
import ChemistryMatrix from '../components/ChemistryMatrix.vue'
import PitchView from '../components/PitchView.vue'

const squadStore = useSquadStore()
const activeSport = ref('soccer')

const sports = [
  { id: 'soccer', label: 'Soccer', icon: '⚽' },
  { id: 'basketball', label: 'Basketball', icon: '🏀' },
  { id: 'cricket', label: 'Cricket', icon: '🏏' },
]

onMounted(() => {
  if (!squadStore.players.length) squadStore.fetchPlayers()
})

const filteredPlayers = computed(() =>
  squadStore.players.filter(p => p.sport === activeSport.value)
)

const sportLabel = computed(() => {
  const s = sports.find(s => s.id === activeSport.value)
  return s ? s.label : ''
})

function sportPlayerCount(sport) {
  return squadStore.players.filter(p => p.sport === sport).length
}

const selectedPlayerObjects = computed(() =>
  squadStore.selectedPlayers
    .map((id) => squadStore.playerMap[id])
    .filter(p => p && p.sport === activeSport.value)
)
</script>
