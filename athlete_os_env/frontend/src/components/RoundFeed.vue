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
      <span :class="eventIcon(event).color" class="shrink-0 mt-0.5">{{ eventIcon(event).icon }}</span>
      <span class="text-gray-300">
        <span class="text-gray-500">R{{ event.round || '?' }}</span>
        {{ event.player || '' }} — {{ event.action || event.type || '' }}
        <span v-if="event.rating" class="text-accent-amber">({{ event.rating.toFixed?.(1) || event.rating }})</span>
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

function eventIcon(event) {
  const type = event.type || event.action || ''
  if (type.includes('goal')) return { icon: '\u26BD', color: 'text-accent-emerald' }
  if (type.includes('drift')) return { icon: '\u26A0', color: 'text-accent-amber' }
  if (type.includes('injury') || type.includes('foul')) return { icon: '\uD83D\uDCA5', color: 'text-accent-rose' }
  return { icon: '\u25B6', color: 'text-accent-cyan' }
}
</script>
