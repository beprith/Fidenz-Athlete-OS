<template>
  <div>
    <!-- Dual Scenario Panels -->
    <div class="grid md:grid-cols-2 gap-4 mb-6">
      <div class="card">
        <h3 class="font-semibold text-accent-cyan mb-3">Scenario A — Current Team</h3>
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
          <button class="btn-primary text-sm flex-1" :disabled="running || episodeStore.done" @click="runStep">
            {{ running ? 'Simulating...' : 'Run Step' }}
          </button>
          <button class="btn-secondary text-sm" :disabled="running || episodeStore.done" @click="runAll">
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
        <h3 class="font-semibold mb-3">Pitch View</h3>
        <PitchView :players="[]" />
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
import RewardChart from './RewardChart.vue'
import RoundFeed from './RoundFeed.vue'
import PitchView from './PitchView.vue'
import AgentThoughtLog from './AgentThoughtLog.vue'

const emit = defineEmits(['next'])
const episodeStore = useEpisodeStore()
const simStore = useSimulationStore()

const running = ref(false)

const lastDrift = computed(() => {
  const kl = episodeStore.klHistory
  return kl.length ? kl[kl.length - 1] : 0
})

async function runStep() {
  running.value = true
  try {
    const result = await episodeStore.step({
      action_type: 'simulate_round',
      player_id: episodeStore.lastObservation?.player_id || 'default',
      target_context: { team: 'Arsenal', formation: '4-3-3', role: 'CF' },
    })
    if (result?.observation) {
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
  while (!episodeStore.done) {
    await runStep()
    await new Promise((r) => setTimeout(r, 200))
  }
  running.value = false
}
</script>
