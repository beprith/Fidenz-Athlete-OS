<template>
  <div>
    <!-- Config Warning -->
    <div v-if="!hasConfig" class="card mb-6 border border-accent-amber/40">
      <p class="text-accent-amber text-sm">No player/team selected. Go back to Step 1 to configure the simulation.</p>
    </div>

    <!-- Dual Scenario Panels -->
    <div class="grid md:grid-cols-2 gap-4 mb-6">
      <div class="card">
        <h3 class="font-semibold text-accent-cyan mb-3">Scenario A — Current Team</h3>
        <div class="text-xs text-gray-500 mb-3" v-if="playerName">
          {{ playerName }} · {{ teamName }} ({{ teamFormation }})
        </div>
        <div class="grid grid-cols-3 gap-4 text-center text-sm mb-4">
          <div>
            <p class="text-gray-500">Round</p>
            <p class="text-lg font-bold">{{ episodeStore.currentRound }} / {{ episodeStore.totalRounds || '—' }}</p>
          </div>
          <div>
            <p class="text-gray-500">Reward</p>
            <p class="text-lg font-bold text-accent-emerald">{{ episodeStore.cumulativeReward.toFixed(3) }}</p>
          </div>
          <div>
            <p class="text-gray-500">Status</p>
            <p class="text-lg font-bold" :class="running ? 'text-accent-cyan' : 'text-gray-400'">{{ running ? 'Running' : 'Idle' }}</p>
          </div>
        </div>
        <div class="flex gap-2">
          <button class="btn-primary text-sm flex-1" :disabled="running || episodeStore.done || !hasConfig" @click="runStep">
            {{ running ? 'Simulating...' : 'Run Step' }}
          </button>
          <button class="btn-secondary text-sm" :disabled="running || episodeStore.done || !hasConfig" @click="runAll">
            Auto-Run All
          </button>
        </div>
      </div>

      <div class="card">
        <h3 class="font-semibold text-accent-amber mb-3">Scenario B — Target Team</h3>
        <div class="grid grid-cols-3 gap-4 text-center text-sm mb-4">
          <div>
            <p class="text-gray-500">Round</p>
            <p class="text-lg font-bold">{{ episodeStore.currentRound }} / {{ episodeStore.totalRounds || '—' }}</p>
          </div>
          <div>
            <p class="text-gray-500">KL Drift</p>
            <p class="text-lg font-bold text-accent-rose">{{ lastDrift.toFixed(4) }}</p>
          </div>
          <div>
            <p class="text-gray-500">Done</p>
            <p class="text-lg font-bold" :class="episodeStore.done ? 'text-accent-emerald' : 'text-gray-400'">{{ episodeStore.done ? 'Yes' : 'No' }}</p>
          </div>
        </div>
        <div class="text-sm text-gray-400">
          <p>{{ episodeStore.playerSummary }}</p>
        </div>
        <div v-if="lastError" class="mt-3 p-2 bg-red-900/20 border border-red-700/40 rounded text-xs text-red-400">
          {{ lastError }}
        </div>
      </div>
    </div>

    <!-- Visualization Row -->
    <div class="grid lg:grid-cols-2 gap-4 mb-6">
      <div class="card">
        <h3 class="font-semibold mb-3">Reward & KL Penalty</h3>
        <RewardChart :rewards="episodeStore.rewardHistory" :kl="episodeStore.klHistory" />
      </div>
      <div class="card">
        <h3 class="font-semibold mb-3">Live Event Feed</h3>
        <RoundFeed :events="simStore.roundEvents" />
      </div>
    </div>

    <!-- Pitch + Agent Log -->
    <div class="grid lg:grid-cols-2 gap-4">
      <div class="card">
        <h3 class="font-semibold mb-3">{{ squadStore.selectedPlayerSport === 'basketball' ? 'Court View' : squadStore.selectedPlayerSport === 'cricket' ? 'Field View' : 'Pitch View' }}</h3>
        <PitchView :players="[]" :sport="squadStore.selectedPlayerSport || 'soccer'" />
      </div>
      <div class="card">
        <h3 class="font-semibold mb-3">Agent Reasoning Log</h3>
        <AgentThoughtLog :log="episodeStore.stepLog" />
      </div>
    </div>

    <div v-if="!episodeStore.done" class="mt-6 flex justify-end">
      <button class="btn-primary" :disabled="!episodeStore.done" @click="$emit('next')">View Report</button>
    </div>
    <div v-else class="mt-6 flex justify-end">
      <button class="btn-primary" @click="$emit('next')">View Report</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useEpisodeStore } from '../store/episode.js'
import { useSimulationStore } from '../store/simulation.js'
import { useSquadStore } from '../store/squad.js'
import RewardChart from './RewardChart.vue'
import RoundFeed from './RoundFeed.vue'
import PitchView from './PitchView.vue'
import AgentThoughtLog from './AgentThoughtLog.vue'

const emit = defineEmits(['next'])
const episodeStore = useEpisodeStore()
const simStore = useSimulationStore()
const squadStore = useSquadStore()

const running = ref(false)
const lastError = ref(null)

const hasConfig = computed(() => !!squadStore.selectedPlayerId && !!squadStore.selectedTeam)

const playerName = computed(() => {
  const p = squadStore.selectedPlayer
  return p ? p.name : ''
})

const teamName = computed(() => {
  const t = squadStore.selectedTeam
  return t ? t.name : ''
})

const teamFormation = computed(() => {
  const t = squadStore.selectedTeam
  return t ? t.formation : ''
})

const lastDrift = computed(() => {
  const kl = episodeStore.klHistory
  return kl.length ? kl[kl.length - 1] : 0
})

function buildAction() {
  const team = squadStore.selectedTeam
  return {
    action_type: 'simulate_round',
    player_id: squadStore.selectedPlayerId || 'default',
    target_context: {
      team: team?.name || 'Arsenal',
      formation: team?.formation || '4-3-3',
      role: team?.role || squadStore.selectedPlayer?.position || 'CF',
    },
  }
}

async function runStep() {
  running.value = true
  lastError.value = null
  try {
    const action = buildAction()
    const result = await episodeStore.step(action)
    if (result?.observation?.last_action_error) {
      lastError.value = result.observation.last_action_error
    } else if (result?.observation) {
      simStore.addRoundEvent({
        round: episodeStore.currentRound,
        player: episodeStore.playerSummary,
        action: 'simulate_round',
        rating: result.observation.performance_metrics?.tactical_fit || 0,
      })
    }
  } finally {
    running.value = false
  }
}

async function runAll() {
  running.value = true
  lastError.value = null
  while (!episodeStore.done) {
    await runStep()
    if (lastError.value) break
    await new Promise((r) => setTimeout(r, 200))
  }
  running.value = false
}
</script>
