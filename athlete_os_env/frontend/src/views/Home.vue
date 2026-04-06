<template>
  <div class="max-w-6xl mx-auto px-4 py-12">
    <!-- Hero -->
    <div class="text-center mb-16">
      <img
        src="/fidenz-labs-logo.png"
        alt="Fidenz Labs"
        class="mx-auto h-24 w-auto object-contain mb-8 drop-shadow-[0_0_24px_rgba(34,211,238,0.15)]"
        width="120"
        height="120"
      />
      <h1 class="text-5xl font-extrabold tracking-tight mb-4">
        <span class="bg-gradient-to-r from-accent-cyan via-accent-emerald to-accent-cyan bg-clip-text text-transparent">
          Fidenz Athlete OS
        </span>
      </h1>
      <p class="text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed">
        Multi-sport player simulation platform powered by swarm agents,
        GraphRAG, and reinforcement learning.
      </p>
    </div>

    <!-- Task Selection -->
    <div class="grid md:grid-cols-3 gap-6 mb-12">
      <div
        v-for="task in tasks"
        :key="task.id"
        class="card cursor-pointer hover:border-accent-cyan/50 transition-all group"
        :class="{ 'border-accent-cyan ring-1 ring-accent-cyan/30': selectedTask === task.id }"
        @click="selectedTask = task.id"
      >
        <div class="flex items-center gap-2 mb-3">
          <span
            class="text-xs font-bold uppercase px-2 py-0.5 rounded"
            :class="difficultyColor(task.difficulty)"
          >
            {{ task.difficulty }}
          </span>
          <span class="text-xs text-gray-500">{{ task.max_steps }} steps</span>
        </div>
        <h3 class="font-semibold mb-2 group-hover:text-accent-cyan transition-colors">
          {{ task.name }}
        </h3>
        <p class="text-sm text-gray-400 leading-relaxed">{{ task.description }}</p>
      </div>
    </div>

    <!-- Player / Sport Selector -->
    <div class="card mb-8">
      <h2 class="text-lg font-semibold mb-4">Configure Simulation</h2>
      <div class="grid md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-400 mb-2">Select Player</label>
          <select v-model="selectedPlayer" @change="onPlayerChange" class="w-full bg-surface-700 border border-surface-600 rounded-lg px-4 py-2.5 text-gray-200 focus:outline-none focus:border-accent-cyan">
            <option value="">Choose a player...</option>
            <optgroup v-for="(group, sport) in playersBySport" :key="sport" :label="sportLabel(sport)">
              <option v-for="p in group" :key="p.player_id" :value="p.player_id">
                {{ p.name }} ({{ p.position }}) — {{ p.nationality }}
              </option>
            </optgroup>
          </select>
          <p v-if="selectedPlayerSport" class="text-xs mt-1.5" :class="sportTextColor(selectedPlayerSport)">
            {{ sportIcon(selectedPlayerSport) }} {{ sportLabel(selectedPlayerSport) }} player
          </p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-400 mb-2">
            Target Team
            <span v-if="selectedPlayerSport" class="text-xs" :class="sportTextColor(selectedPlayerSport)">
              ({{ sportLabel(selectedPlayerSport) }} only)
            </span>
          </label>
          <select v-model="selectedTeam" :disabled="!selectedPlayer" class="w-full bg-surface-700 border border-surface-600 rounded-lg px-4 py-2.5 text-gray-200 focus:outline-none focus:border-accent-cyan disabled:opacity-50">
            <option value="">{{ selectedPlayer ? 'Choose a team...' : 'Select a player first' }}</option>
            <option v-for="t in filteredTeams" :key="t.id" :value="t.id">
              {{ t.name }} — {{ t.league }} ({{ t.formation }})
            </option>
          </select>
          <p v-if="selectedPlayer && !filteredTeams.length" class="text-xs text-accent-rose mt-1.5">
            No teams available for this sport
          </p>
        </div>
      </div>

      <div class="mt-6">
        <label class="block text-sm font-medium text-gray-400 mb-2">Scenario Description (optional)</label>
        <textarea
          v-model="scenario"
          rows="3"
          placeholder='e.g. "Sign Kylian Mbappé to Arsenal playing as a false 9 in a 4-2-3-1"'
          class="w-full bg-surface-700 border border-surface-600 rounded-lg px-4 py-2.5 text-gray-200 placeholder-gray-500 focus:outline-none focus:border-accent-cyan resize-none"
        ></textarea>
      </div>

      <!-- Upload -->
      <div class="mt-6">
        <label class="block text-sm font-medium text-gray-400 mb-2">Upload Stats (CSV/JSON)</label>
        <div
          class="border-2 border-dashed border-surface-600 rounded-lg p-8 text-center hover:border-accent-cyan/50 transition-colors cursor-pointer"
          @dragover.prevent
          @drop.prevent="handleDrop"
          @click="$refs.fileInput.click()"
        >
          <p class="text-gray-400 text-sm">Drag and drop a file or click to browse</p>
          <p v-if="uploadedFile" class="text-accent-emerald text-sm mt-2">{{ uploadedFile.name }}</p>
          <input ref="fileInput" type="file" class="hidden" accept=".csv,.json" @change="handleFile" />
        </div>
      </div>
    </div>

    <!-- Launch Button -->
    <div class="text-center">
      <button
        class="btn-primary text-lg px-10 py-3 disabled:opacity-40"
        :disabled="!selectedTask || loading"
        @click="launchSimulation"
      >
        {{ loading ? 'Initializing...' : 'Launch Simulation' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useEpisodeStore } from '../store/episode.js'
import { useSquadStore } from '../store/squad.js'
import { useSimulationStore } from '../store/simulation.js'
import { getTasks } from '../api/simulation.js'

const router = useRouter()
const episodeStore = useEpisodeStore()
const squadStore = useSquadStore()
const simStore = useSimulationStore()

const tasks = ref([])
const selectedTask = ref('single_player_stat_prediction')
const selectedPlayer = ref('')
const selectedTeam = ref('')
const scenario = ref('')
const uploadedFile = ref(null)
const loading = ref(false)

onMounted(async () => {
  try {
    tasks.value = await getTasks()
    await squadStore.fetchPlayers()
    await squadStore.fetchTeams()
  } catch {
    tasks.value = [
      { id: 'single_player_stat_prediction', name: 'Single Player Stat Prediction', difficulty: 'easy', max_steps: 10, description: 'Predict whether a player\'s key metric will be above or below career mean.' },
      { id: 'player_team_fit_analysis', name: 'Player-Team Tactical Fit', difficulty: 'medium', max_steps: 20, description: 'Simulate match rounds and score tactical fit and contribution.' },
      { id: 'full_squad_recruitment_sim', name: 'Full Squad Recruitment Sim', difficulty: 'hard', max_steps: 50, description: 'Simulate a full season for an 11-player squad.' },
    ]
  }
})

const selectedPlayerSport = computed(() => {
  if (!selectedPlayer.value) return null
  const p = squadStore.players.find(p => p.player_id === selectedPlayer.value)
  return p ? p.sport : null
})

const playersBySport = computed(() => {
  const groups = {}
  for (const p of squadStore.players) {
    const s = p.sport || 'other'
    if (!groups[s]) groups[s] = []
    groups[s].push(p)
  }
  return groups
})

const filteredTeams = computed(() => {
  if (!selectedPlayerSport.value) return squadStore.teams
  return squadStore.teams.filter(t => t.sport === selectedPlayerSport.value)
})

function onPlayerChange() {
  selectedTeam.value = ''
  if (selectedPlayer.value) {
    squadStore.selectPlayer(selectedPlayer.value)
  }
}

function sportLabel(sport) {
  const labels = { soccer: 'Soccer', basketball: 'Basketball', cricket: 'Cricket' }
  return labels[sport] || sport
}

function sportIcon(sport) {
  const icons = { soccer: '⚽', basketball: '🏀', cricket: '🏏' }
  return icons[sport] || '🎯'
}

function sportTextColor(sport) {
  const cls = { soccer: 'text-green-400', basketball: 'text-orange-400', cricket: 'text-blue-400' }
  return cls[sport] || 'text-gray-400'
}

function difficultyColor(d) {
  const m = { easy: 'bg-accent-emerald/20 text-accent-emerald', medium: 'bg-accent-amber/20 text-accent-amber', hard: 'bg-accent-rose/20 text-accent-rose' }
  return m[d] || 'bg-gray-700 text-gray-400'
}

function handleFile(e) {
  uploadedFile.value = e.target.files[0] || null
}
function handleDrop(e) {
  uploadedFile.value = e.dataTransfer.files[0] || null
}

async function launchSimulation() {
  loading.value = true
  try {
    if (selectedPlayer.value) {
      await squadStore.selectPlayer(selectedPlayer.value)
      const team = filteredTeams.value.find(t => t.id === selectedTeam.value)
      if (team) squadStore.selectTeam(team)
    }
    await episodeStore.reset(selectedTask.value)
    simStore.resetSim()
    simStore.setPhase(1)
    router.push('/workspace')
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>
