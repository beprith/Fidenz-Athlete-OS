<template>
  <div class="card">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold">Step 2 — Persona Forge</h2>
      <span class="text-sm text-gray-400">
        {{ generatedCount }} / {{ totalExpected }} agents generated
      </span>
    </div>
    <p class="text-gray-400 text-sm mb-6">
      AI-generated behavioral personas with trait profiles, decision styles, and MBTI tags.
    </p>

    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      <PlayerCard
        v-for="player in players"
        :key="player.player_id"
        :player="player"
        :show-traits="true"
        @click="expandedPlayer = player"
      />
    </div>

    <!-- Expanded Detail Modal -->
    <div
      v-if="expandedPlayer"
      class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      @click.self="expandedPlayer = null"
    >
      <div class="card max-w-lg w-full max-h-[80vh] overflow-y-auto">
        <div class="flex justify-between items-start mb-4">
          <h3 class="text-lg font-bold">{{ expandedPlayer.name }}</h3>
          <button class="text-gray-400 hover:text-white" @click="expandedPlayer = null">✕</button>
        </div>
        <p class="text-sm text-gray-400 mb-4">{{ expandedPlayer.bio }}</p>
        <div class="grid grid-cols-2 gap-2 text-sm">
          <div><span class="text-gray-500">Position:</span> {{ expandedPlayer.position }}</div>
          <div><span class="text-gray-500">Nationality:</span> {{ expandedPlayer.nationality }}</div>
          <div><span class="text-gray-500">Age:</span> {{ expandedPlayer.age }}</div>
          <div><span class="text-gray-500">MBTI:</span> {{ expandedPlayer.mbti_tag }}</div>
          <div><span class="text-gray-500">Decision:</span> {{ expandedPlayer.decision_style }}</div>
          <div><span class="text-gray-500">Pressure:</span> {{ expandedPlayer.pressure_response }}</div>
        </div>
        <h4 class="font-semibold mt-4 mb-2 text-sm">Trait Vector</h4>
        <div class="space-y-1">
          <div v-for="trait in traitList" :key="trait.name" class="flex items-center gap-2 text-xs">
            <span class="w-28 text-gray-400 truncate">{{ trait.label }}</span>
            <div class="flex-1 bg-surface-700 rounded-full h-2">
              <div
                class="h-2 rounded-full bg-gradient-to-r from-accent-cyan to-accent-emerald"
                :style="{ width: (trait.value * 100) + '%' }"
              ></div>
            </div>
            <span class="w-8 text-right text-gray-500">{{ (trait.value * 100).toFixed(0) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="flex justify-end">
      <button class="btn-primary" @click="$emit('next')">Continue to Graph View</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSquadStore } from '../store/squad.js'
import PlayerCard from './PlayerCard.vue'

const emit = defineEmits(['next'])
const squadStore = useSquadStore()

const expandedPlayer = ref(null)
const generatedCount = computed(() => squadStore.players.length)
const totalExpected = computed(() => squadStore.players.length || 7)

onMounted(() => {
  if (!squadStore.players.length) squadStore.fetchPlayers()
})

const players = computed(() => squadStore.players)

const TRAIT_LABELS = {
  speed: 'Speed', stamina: 'Stamina', positioning: 'Positioning', technical: 'Technical',
  aerial: 'Aerial', decision_speed: 'Decision Speed', pressure_tolerance: 'Pressure Tol.',
  creativity: 'Creativity', work_rate: 'Work Rate', leadership: 'Leadership',
  consistency: 'Consistency', injury_resilience: 'Injury Resil.', form_momentum: 'Form',
  big_game_performance: 'Big Game', adaptability: 'Adaptability', teamwork: 'Teamwork',
}

const traitList = computed(() => {
  if (!expandedPlayer.value) return []
  return Object.entries(TRAIT_LABELS).map(([key, label]) => ({
    name: key,
    label,
    value: expandedPlayer.value[key] || 0.5,
  }))
})
</script>
