<template>
  <div class="card">
    <h2 class="text-xl font-semibold mb-4">Step 1 — Simulation Configuration</h2>
    <p class="text-gray-400 text-sm mb-6">
      Select a player and target team to configure the simulation. Teams are filtered to match the player's sport.
    </p>

    <!-- Player Selection -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-400 mb-2">Select Player</label>
      <div v-if="loading" class="text-gray-500 text-sm">Loading players...</div>
      <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
        <div
          v-for="player in players"
          :key="player.player_id"
          class="relative rounded-lg border-2 p-3 cursor-pointer transition-all"
          :class="selectedPlayerId === player.player_id
            ? 'border-accent-cyan bg-accent-cyan/10'
            : 'border-surface-600 bg-surface-700 hover:border-surface-500'"
          @click="onSelectPlayer(player.player_id)"
        >
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold shrink-0"
              :class="sportBadgeClass(player.sport)"
            >
              {{ sportIcon(player.sport) }}
            </div>
            <div class="min-w-0">
              <p class="font-medium text-gray-200 truncate">{{ player.name }}</p>
              <p class="text-xs text-gray-500">{{ player.position }} · {{ player.nationality }}</p>
              <span
                class="inline-block mt-1 text-[10px] px-1.5 py-0.5 rounded-full font-medium uppercase tracking-wide"
                :class="sportTagClass(player.sport)"
              >
                {{ player.sport }}
              </span>
            </div>
          </div>
          <div v-if="selectedPlayerId === player.player_id" class="absolute top-1.5 right-1.5 text-accent-cyan text-sm">✓</div>
        </div>
      </div>
    </div>

    <!-- Team Selection (only shown after player is selected) -->
    <div v-if="selectedPlayerId" class="mb-6">
      <label class="block text-sm font-medium text-gray-400 mb-2">
        Select Target Team
        <span v-if="selectedSport" class="text-accent-cyan">({{ selectedSport }} teams only)</span>
      </label>

      <div v-if="compatibleTeams.length === 0" class="text-gray-500 text-sm">Loading compatible teams...</div>
      <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <div
          v-for="team in compatibleTeams"
          :key="team.id"
          class="rounded-lg border-2 p-3 cursor-pointer transition-all"
          :class="selectedTeamId === team.id
            ? 'border-accent-emerald bg-accent-emerald/10'
            : 'border-surface-600 bg-surface-700 hover:border-surface-500'"
          @click="onSelectTeam(team)"
        >
          <p class="font-medium text-gray-200">{{ team.name }}</p>
          <p class="text-xs text-gray-500 mt-1">{{ team.league }} · {{ team.formation }} · {{ team.style }}</p>
        </div>
      </div>

      <!-- Incompatible teams notice -->
      <div v-if="incompatibleTeams.length > 0" class="mt-4">
        <p class="text-xs text-gray-600 mb-2">Unavailable teams (different sport):</p>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="team in incompatibleTeams"
            :key="team.id"
            class="text-xs px-2 py-1 bg-surface-800 text-gray-600 rounded line-through"
          >
            {{ team.name }} ({{ team.sport }})
          </span>
        </div>
      </div>
    </div>

    <!-- Role / Formation Override (soccer-specific) -->
    <div v-if="selectedTeamId && selectedSport === 'soccer'" class="mb-6">
      <label class="block text-sm font-medium text-gray-400 mb-2">Player Role in Team</label>
      <select v-model="selectedRole" class="w-full max-w-xs bg-surface-700 border border-surface-600 rounded-lg px-4 py-2.5 text-gray-200 focus:outline-none focus:border-accent-cyan">
        <option v-for="role in soccerRoles" :key="role" :value="role">{{ role }}</option>
      </select>
    </div>

    <!-- Summary -->
    <div v-if="isConfigComplete" class="mb-6 p-4 rounded-lg bg-surface-700 border border-accent-cyan/30">
      <h3 class="text-sm font-semibold text-accent-cyan mb-2">Configuration Summary</h3>
      <div class="grid grid-cols-2 gap-2 text-sm">
        <div><span class="text-gray-500">Player:</span> <span class="text-gray-200">{{ selectedPlayerName }}</span></div>
        <div><span class="text-gray-500">Sport:</span> <span class="text-gray-200 capitalize">{{ selectedSport }}</span></div>
        <div><span class="text-gray-500">Target Team:</span> <span class="text-gray-200">{{ selectedTeamName }}</span></div>
        <div><span class="text-gray-500">Formation:</span> <span class="text-gray-200">{{ selectedTeamFormation }}</span></div>
      </div>
    </div>

    <div class="flex justify-end">
      <button
        class="btn-primary"
        :disabled="!isConfigComplete"
        :class="{ 'opacity-50 cursor-not-allowed': !isConfigComplete }"
        @click="$emit('next')"
      >
        Continue to Persona Forge
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useSquadStore } from '../store/squad.js'

const emit = defineEmits(['next'])
const squadStore = useSquadStore()

const selectedRole = ref('CF')
const selectedTeamId = ref(null)

const soccerRoles = ['GK', 'CB', 'LB', 'RB', 'CDM', 'CM', 'CAM', 'LW', 'RW', 'CF', 'ST']

const loading = computed(() => squadStore.loading)
const players = computed(() => squadStore.players)
const selectedPlayerId = computed(() => squadStore.selectedPlayerId)
const compatibleTeams = computed(() => squadStore.compatibleTeams)

const selectedSport = computed(() => squadStore.selectedPlayerSport)

const selectedPlayerName = computed(() => {
  const p = squadStore.selectedPlayer
  return p ? p.name : ''
})

const selectedTeamName = computed(() => {
  const t = squadStore.selectedTeam
  return t ? t.name : ''
})

const selectedTeamFormation = computed(() => {
  const t = squadStore.selectedTeam
  return t ? t.formation : ''
})

const incompatibleTeams = computed(() => {
  if (!selectedSport.value) return []
  return squadStore.teams.filter(t => t.sport !== selectedSport.value)
})

const isConfigComplete = computed(() => {
  return selectedPlayerId.value && selectedTeamId.value
})

onMounted(async () => {
  if (!squadStore.players.length) await squadStore.fetchPlayers()
  if (!squadStore.teams.length) await squadStore.fetchTeams()
})

async function onSelectPlayer(playerId) {
  selectedTeamId.value = null
  await squadStore.selectPlayer(playerId)
}

function onSelectTeam(team) {
  selectedTeamId.value = team.id
  squadStore.selectTeam({
    ...team,
    role: selectedRole.value,
  })
}

watch(selectedRole, (role) => {
  if (squadStore.selectedTeam) {
    squadStore.selectTeam({
      ...squadStore.selectedTeam,
      role,
    })
  }
})

function sportIcon(sport) {
  const icons = { soccer: '⚽', basketball: '🏀', cricket: '🏏' }
  return icons[sport] || '🎯'
}

function sportBadgeClass(sport) {
  const cls = {
    soccer: 'bg-green-900/50 text-green-400',
    basketball: 'bg-orange-900/50 text-orange-400',
    cricket: 'bg-blue-900/50 text-blue-400',
  }
  return cls[sport] || 'bg-surface-600 text-gray-400'
}

function sportTagClass(sport) {
  const cls = {
    soccer: 'bg-green-900/40 text-green-400',
    basketball: 'bg-orange-900/40 text-orange-400',
    cricket: 'bg-blue-900/40 text-blue-400',
  }
  return cls[sport] || 'bg-surface-600 text-gray-400'
}
</script>
