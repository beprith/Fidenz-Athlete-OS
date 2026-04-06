<template>
  <div class="relative rounded-lg border overflow-hidden" :class="fieldBorder" style="aspect-ratio: 3/2">
    <!-- Soccer Pitch -->
    <svg v-if="sport === 'soccer'" viewBox="0 0 600 400" class="w-full h-full bg-emerald-900/30">
      <rect x="10" y="10" width="580" height="380" fill="none" stroke="#166534" stroke-width="2" rx="4" />
      <line x1="300" y1="10" x2="300" y2="390" stroke="#166534" stroke-width="1.5" />
      <circle cx="300" cy="200" r="50" fill="none" stroke="#166534" stroke-width="1.5" />
      <circle cx="300" cy="200" r="3" fill="#166534" />
      <rect x="10" y="115" width="100" height="170" fill="none" stroke="#166534" stroke-width="1.5" />
      <rect x="490" y="115" width="100" height="170" fill="none" stroke="#166534" stroke-width="1.5" />
      <rect x="10" y="155" width="40" height="90" fill="none" stroke="#166534" stroke-width="1" />
      <rect x="550" y="155" width="40" height="90" fill="none" stroke="#166534" stroke-width="1" />
      <g v-for="(pos, idx) in positions" :key="idx">
        <circle :cx="pos.x" :cy="pos.y" r="14" :fill="pos.color" stroke="#fff" stroke-width="1.5" opacity="0.9" />
        <text :x="pos.x" :y="pos.y + 4" text-anchor="middle" fill="white" font-size="9" font-weight="bold">{{ pos.label }}</text>
      </g>
    </svg>

    <!-- Basketball Court -->
    <svg v-else-if="sport === 'basketball'" viewBox="0 0 600 400" class="w-full h-full bg-amber-900/20">
      <rect x="10" y="10" width="580" height="380" fill="none" stroke="#92400e" stroke-width="2" rx="4" />
      <line x1="300" y1="10" x2="300" y2="390" stroke="#92400e" stroke-width="1.5" />
      <circle cx="300" cy="200" r="40" fill="none" stroke="#92400e" stroke-width="1.5" />
      <!-- Three-point arcs -->
      <path d="M 10 120 Q 130 200 10 280" fill="none" stroke="#92400e" stroke-width="1.5" />
      <path d="M 590 120 Q 470 200 590 280" fill="none" stroke="#92400e" stroke-width="1.5" />
      <!-- Free-throw lanes -->
      <rect x="10" y="140" width="120" height="120" fill="none" stroke="#92400e" stroke-width="1" />
      <rect x="470" y="140" width="120" height="120" fill="none" stroke="#92400e" stroke-width="1" />
      <!-- Baskets -->
      <circle cx="35" cy="200" r="8" fill="none" stroke="#f59e0b" stroke-width="2" />
      <circle cx="565" cy="200" r="8" fill="none" stroke="#f59e0b" stroke-width="2" />
      <g v-for="(pos, idx) in positions" :key="idx">
        <circle :cx="pos.x" :cy="pos.y" r="14" :fill="pos.color" stroke="#fff" stroke-width="1.5" opacity="0.9" />
        <text :x="pos.x" :y="pos.y + 4" text-anchor="middle" fill="white" font-size="9" font-weight="bold">{{ pos.label }}</text>
      </g>
    </svg>

    <!-- Cricket Field -->
    <svg v-else viewBox="0 0 600 400" class="w-full h-full bg-emerald-950/30">
      <!-- Oval boundary -->
      <ellipse cx="300" cy="200" rx="280" ry="185" fill="none" stroke="#166534" stroke-width="2" />
      <!-- Inner circle (30-yard) -->
      <ellipse cx="300" cy="200" rx="140" ry="95" fill="none" stroke="#166534" stroke-width="1" stroke-dasharray="6 4" />
      <!-- Pitch strip -->
      <rect x="280" y="140" width="40" height="120" fill="#92400e" fill-opacity="0.3" stroke="#92400e" stroke-width="1" rx="2" />
      <!-- Crease lines -->
      <line x1="270" y1="155" x2="330" y2="155" stroke="#fff" stroke-width="1" opacity="0.6" />
      <line x1="270" y1="245" x2="330" y2="245" stroke="#fff" stroke-width="1" opacity="0.6" />
      <!-- Stumps -->
      <rect x="296" y="148" width="8" height="4" fill="#f59e0b" rx="1" />
      <rect x="296" y="248" width="8" height="4" fill="#f59e0b" rx="1" />
      <g v-for="(pos, idx) in positions" :key="idx">
        <circle :cx="pos.x" :cy="pos.y" r="14" :fill="pos.color" stroke="#fff" stroke-width="1.5" opacity="0.9" />
        <text :x="pos.x" :y="pos.y + 4" text-anchor="middle" fill="white" font-size="9" font-weight="bold">{{ pos.label }}</text>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  players: { type: Array, default: () => [] },
  sport: { type: String, default: 'soccer' },
  formation: { type: String, default: '4-3-3' },
})

const SOCCER_POSITIONS = [
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

const BASKETBALL_POSITIONS = [
  { x: 180, y: 200, label: 'PG', color: '#06b6d4' },
  { x: 280, y: 120, label: 'SG', color: '#8b5cf6' },
  { x: 280, y: 280, label: 'SF', color: '#f59e0b' },
  { x: 400, y: 140, label: 'PF', color: '#10b981' },
  { x: 400, y: 260, label: 'C', color: '#f43f5e' },
]

const CRICKET_POSITIONS = [
  { x: 300, y: 165, label: 'BAT', color: '#06b6d4' },
  { x: 300, y: 235, label: 'BWL', color: '#f43f5e' },
  { x: 300, y: 310, label: 'WK', color: '#f59e0b' },
  { x: 180, y: 110, label: 'SLP', color: '#10b981' },
  { x: 420, y: 110, label: 'GUL', color: '#10b981' },
  { x: 140, y: 200, label: 'MID', color: '#8b5cf6' },
  { x: 460, y: 200, label: 'MID', color: '#8b5cf6' },
  { x: 180, y: 300, label: 'FIN', color: '#10b981' },
  { x: 420, y: 300, label: 'LEG', color: '#10b981' },
  { x: 100, y: 100, label: 'BDY', color: '#8b5cf6' },
  { x: 500, y: 100, label: 'PT', color: '#8b5cf6' },
]

const defaultPositions = computed(() => {
  if (props.sport === 'basketball') return BASKETBALL_POSITIONS
  if (props.sport === 'cricket') return CRICKET_POSITIONS
  return SOCCER_POSITIONS
})

const positions = computed(() => {
  if (props.players.length) {
    return props.players.map((p, i) => {
      const def = defaultPositions.value[i] || defaultPositions.value[0]
      return { ...def, label: p.position || def.label }
    })
  }
  return defaultPositions.value
})

const fieldBorder = computed(() => {
  if (props.sport === 'basketball') return 'border-amber-800/40'
  if (props.sport === 'cricket') return 'border-emerald-800/40'
  return 'border-emerald-800/40'
})
</script>
