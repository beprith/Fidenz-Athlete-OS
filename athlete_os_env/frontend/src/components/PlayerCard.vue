<template>
  <div
    class="card cursor-pointer hover:border-accent-cyan/40 transition-all group relative"
    :class="{ 'border-accent-cyan ring-1 ring-accent-cyan/20': selected }"
    @click="$emit('click')"
  >
    <!-- Avatar + Name -->
    <div class="flex items-center gap-3 mb-3">
      <div
        class="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold"
        :style="{ background: positionColor }"
      >
        {{ initials }}
      </div>
      <div class="flex-1 min-w-0">
        <h4 class="font-semibold text-sm truncate group-hover:text-accent-cyan transition-colors">
          {{ player.name }}
        </h4>
        <p class="text-xs text-gray-500">{{ player.position }} · {{ player.nationality }}</p>
      </div>
      <span v-if="player.mbti_tag" class="text-[10px] bg-surface-700 px-1.5 py-0.5 rounded text-gray-400">
        {{ player.mbti_tag }}
      </span>
    </div>

    <!-- Key traits (3 bars) -->
    <div v-if="showTraits" class="space-y-1.5">
      <div v-for="trait in keyTraits" :key="trait.name" class="flex items-center gap-2 text-xs">
        <span class="w-16 text-gray-500 truncate">{{ trait.label }}</span>
        <div class="flex-1 bg-surface-700 rounded-full h-1.5">
          <div
            class="h-1.5 rounded-full"
            :class="trait.color"
            :style="{ width: (trait.value * 100) + '%' }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Drift badge -->
    <div v-if="drift > 0.1" class="absolute top-2 right-2">
      <span class="text-[10px] bg-accent-rose/20 text-accent-rose px-1.5 py-0.5 rounded-full">
        drift {{ drift.toFixed(2) }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  player: { type: Object, required: true },
  selected: { type: Boolean, default: false },
  showTraits: { type: Boolean, default: true },
  drift: { type: Number, default: 0 },
})

defineEmits(['click'])

const initials = computed(() => {
  const parts = (props.player.name || '').split(' ')
  return parts.map((p) => p[0]).join('').slice(0, 2).toUpperCase()
})

const positionColor = computed(() => {
  const m = {
    GK: '#f59e0b', CB: '#10b981', LB: '#10b981', RB: '#10b981',
    CDM: '#8b5cf6', CM: '#8b5cf6', CAM: '#06b6d4',
    LW: '#f43f5e', RW: '#f43f5e', CF: '#f43f5e', ST: '#f43f5e',
    SF: '#06b6d4', Batsman: '#f59e0b',
  }
  return m[props.player.position] || '#6b7280'
})

const keyTraits = computed(() => {
  const p = props.player
  return [
    { name: 'speed', label: 'Speed', value: p.speed || 0.5, color: 'bg-accent-cyan' },
    { name: 'technical', label: 'Technical', value: p.technical || 0.5, color: 'bg-accent-emerald' },
    { name: 'big_game', label: 'Big Game', value: p.big_game_performance || 0.5, color: 'bg-accent-amber' },
  ]
})
</script>
