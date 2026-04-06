<template>
  <div class="h-64 overflow-y-auto space-y-1 font-mono text-xs" ref="feedContainer">
    <div v-if="!events.length" class="text-gray-500 text-center py-8 font-sans text-sm">
      Waiting for simulation events...
    </div>
    <div
      v-for="(event, idx) in events"
      :key="idx"
      class="flex items-start gap-2 py-1 px-2 rounded hover:bg-surface-700/50"
    >
      <span :class="eventDisplay(event).color" class="shrink-0 mt-0.5">{{ eventDisplay(event).icon }}</span>
      <span class="text-gray-300">
        <span class="text-gray-500">R{{ event.round || '?' }}</span>
        {{ event.player || '' }} — {{ event.action || event.type || '' }}
        <span v-if="event.rating" class="text-accent-amber">({{ typeof event.rating === 'number' ? event.rating.toFixed(1) : event.rating }})</span>
      </span>
    </div>
  </div>
</template>

<script setup>
import { watch, ref, nextTick } from 'vue'

const props = defineProps({
  events: { type: Array, default: () => [] },
})

const feedContainer = ref(null)

watch(() => props.events.length, async () => {
  await nextTick()
  if (feedContainer.value) {
    feedContainer.value.scrollTop = feedContainer.value.scrollHeight
  }
})

const EVENT_ICONS = {
  // Soccer
  goal: { icon: '⚽', color: 'text-accent-emerald' },
  assist: { icon: '🎯', color: 'text-accent-cyan' },
  shot: { icon: '💨', color: 'text-gray-400' },
  pass: { icon: '➡', color: 'text-gray-500' },
  key_pass: { icon: '🔑', color: 'text-accent-cyan' },
  tackle: { icon: '🦵', color: 'text-accent-amber' },
  intercept: { icon: '🛡', color: 'text-accent-amber' },
  dribble: { icon: '⚡', color: 'text-accent-cyan' },
  cross: { icon: '↗', color: 'text-gray-400' },
  header: { icon: '🗣', color: 'text-gray-400' },
  save: { icon: '🧤', color: 'text-accent-emerald' },
  foul: { icon: '🟨', color: 'text-accent-rose' },

  // Basketball
  two_pointer: { icon: '🏀', color: 'text-accent-emerald' },
  three_pointer: { icon: '🎯', color: 'text-accent-cyan' },
  free_throw: { icon: '🏀', color: 'text-gray-400' },
  rebound: { icon: '📥', color: 'text-accent-amber' },
  steal: { icon: '⚡', color: 'text-accent-cyan' },
  block: { icon: '🛡', color: 'text-accent-amber' },
  turnover: { icon: '❌', color: 'text-accent-rose' },
  dunk: { icon: '💥', color: 'text-accent-emerald' },
  layup: { icon: '🏀', color: 'text-accent-emerald' },

  // Cricket
  single: { icon: '🏏', color: 'text-gray-400' },
  boundary: { icon: '4️⃣', color: 'text-accent-cyan' },
  six: { icon: '6️⃣', color: 'text-accent-emerald' },
  dot_ball: { icon: '⏺', color: 'text-gray-500' },
  wicket: { icon: '🎳', color: 'text-accent-rose' },
  catch: { icon: '🤲', color: 'text-accent-amber' },
  run_out: { icon: '🏃', color: 'text-accent-rose' },
  stumping: { icon: '⚡', color: 'text-accent-amber' },
  wide: { icon: 'W', color: 'text-accent-rose' },
  no_ball: { icon: 'NB', color: 'text-accent-rose' },
  maiden_over: { icon: 'M', color: 'text-accent-emerald' },

  // Generic
  simulate_round: { icon: '▶', color: 'text-accent-cyan' },
  drift: { icon: '⚠', color: 'text-accent-amber' },
  injury: { icon: '🏥', color: 'text-accent-rose' },
}

function eventDisplay(event) {
  const type = event.type || event.action || ''
  return EVENT_ICONS[type] || { icon: '▶', color: 'text-accent-cyan' }
}
</script>
