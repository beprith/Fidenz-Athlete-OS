<template>
  <div class="relative bg-emerald-900/30 rounded-lg border border-emerald-800/40 overflow-hidden" style="aspect-ratio: 3/2">
    <svg viewBox="0 0 600 400" class="w-full h-full">
      <!-- Pitch outline -->
      <rect x="10" y="10" width="580" height="380" fill="none" stroke="#166534" stroke-width="2" rx="4" />
      <!-- Center line -->
      <line x1="300" y1="10" x2="300" y2="390" stroke="#166534" stroke-width="1.5" />
      <!-- Center circle -->
      <circle cx="300" cy="200" r="50" fill="none" stroke="#166534" stroke-width="1.5" />
      <circle cx="300" cy="200" r="3" fill="#166534" />
      <!-- Penalty areas -->
      <rect x="10" y="115" width="100" height="170" fill="none" stroke="#166534" stroke-width="1.5" />
      <rect x="490" y="115" width="100" height="170" fill="none" stroke="#166534" stroke-width="1.5" />
      <!-- Goal areas -->
      <rect x="10" y="155" width="40" height="90" fill="none" stroke="#166534" stroke-width="1" />
      <rect x="550" y="155" width="40" height="90" fill="none" stroke="#166534" stroke-width="1" />

      <!-- Player dots -->
      <g v-for="(pos, idx) in playerPositions" :key="idx">
        <circle
          :cx="pos.x" :cy="pos.y" r="14"
          :fill="pos.color"
          stroke="#fff"
          stroke-width="1.5"
          opacity="0.9"
        />
        <text :x="pos.x" :y="pos.y + 4" text-anchor="middle" fill="white" font-size="9" font-weight="bold">
          {{ pos.label }}
        </text>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  players: { type: Array, default: () => [] },
  formation: { type: String, default: '4-3-3' },
})

const DEFAULT_POSITIONS_433 = [
  { x: 50, y: 200, label: 'GK', color: '#f59e0b' },
  { x: 140, y: 100, label: 'LB', color: '#10b981' },
  { x: 140, y: 170, label: 'CB', color: '#10b981' },
  { x: 140, y: 230, label: 'CB', color: '#10b981' },
  { x: 140, y: 300, label: 'RB', color: '#10b981' },
  { x: 300, y: 120, label: 'CM', color: '#8b5cf6' },
  { x: 300, y: 200, label: 'CM', color: '#8b5cf6' },
  { x: 300, y: 280, label: 'CM', color: '#8b5cf6' },
  { x: 470, y: 100, label: 'LW', color: '#f43f5e' },
  { x: 490, y: 200, label: 'CF', color: '#f43f5e' },
  { x: 470, y: 300, label: 'RW', color: '#f43f5e' },
]

const playerPositions = computed(() => {
  if (props.players.length) {
    return props.players.map((p, i) => {
      const def = DEFAULT_POSITIONS_433[i] || DEFAULT_POSITIONS_433[0]
      return { ...def, label: p.position || def.label }
    })
  }
  return DEFAULT_POSITIONS_433
})
</script>
