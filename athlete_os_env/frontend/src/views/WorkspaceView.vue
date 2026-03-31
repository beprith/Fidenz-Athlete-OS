<template>
  <div class="max-w-7xl mx-auto px-4 py-6">
    <!-- Step Navigation -->
    <div class="flex items-center gap-4 mb-8 overflow-x-auto pb-2">
      <div
        v-for="phase in simStore.phases"
        :key="phase.id"
        class="flex items-center gap-2 cursor-pointer shrink-0"
        @click="simStore.setPhase(phase.id)"
      >
        <span
          :class="[
            phase.status === 'done' ? 'step-badge-done' : phase.status === 'active' ? 'step-badge-active' : 'step-badge-pending'
          ]"
        >
          {{ phase.status === 'done' ? '✓' : phase.id }}
        </span>
        <span
          class="text-sm font-medium"
          :class="phase.status === 'active' ? 'text-accent-cyan' : phase.status === 'done' ? 'text-accent-emerald' : 'text-gray-500'"
        >
          {{ phase.name }}
        </span>
        <div v-if="phase.id < 5" class="w-8 h-px bg-surface-600"></div>
      </div>
    </div>

    <!-- Active Step Content -->
    <Step1DataIngest v-if="simStore.activePhase === 1" @next="simStore.setPhase(2)" />
    <Step2PersonaForge v-else-if="simStore.activePhase === 2" @next="simStore.setPhase(3)" />
    <Step3GraphView v-else-if="simStore.activePhase === 3" @next="simStore.setPhase(4)" />
    <Step4SimRunner v-else-if="simStore.activePhase === 4" @next="simStore.setPhase(5)" />
    <Step5Report v-else-if="simStore.activePhase === 5" />

    <!-- Bottom Status Bar -->
    <div class="mt-8 card flex items-center justify-between text-sm">
      <div class="flex items-center gap-6">
        <span class="text-gray-400">Task: <span class="text-gray-200">{{ episodeStore.taskId }}</span></span>
        <span class="text-gray-400">Step: <span class="text-gray-200">{{ episodeStore.stepCount }}</span></span>
        <span class="text-gray-400">Reward: <span class="text-accent-emerald">{{ episodeStore.cumulativeReward.toFixed(3) }}</span></span>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-gray-400">Status:</span>
        <span :class="statusColor">{{ episodeStore.simulationStatus }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useEpisodeStore } from '../store/episode.js'
import { useSimulationStore } from '../store/simulation.js'
import Step1DataIngest from '../components/Step1DataIngest.vue'
import Step2PersonaForge from '../components/Step2PersonaForge.vue'
import Step3GraphView from '../components/Step3GraphView.vue'
import Step4SimRunner from '../components/Step4SimRunner.vue'
import Step5Report from '../components/Step5Report.vue'

const episodeStore = useEpisodeStore()
const simStore = useSimulationStore()

const statusColor = computed(() => {
  const m = {
    idle: 'text-gray-400',
    building: 'text-accent-amber',
    simulating: 'text-accent-cyan',
    grading: 'text-accent-violet',
    done: 'text-accent-emerald',
  }
  return m[episodeStore.simulationStatus] || 'text-gray-400'
})
</script>
