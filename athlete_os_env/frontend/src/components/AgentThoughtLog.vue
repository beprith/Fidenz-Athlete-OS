<template>
  <div class="h-64 overflow-y-auto space-y-2 text-sm" ref="logContainer">
    <div v-if="!log.length" class="text-gray-500 text-center py-8">
      No agent reasoning steps yet.
    </div>
    <div
      v-for="(entry, idx) in log"
      :key="idx"
      class="bg-surface-700/50 rounded-lg p-3"
    >
      <div class="flex items-center gap-2 mb-1">
        <span class="text-accent-cyan font-mono text-xs">Step {{ entry.step }}</span>
        <span class="text-gray-600">|</span>
        <span class="text-xs text-gray-400">{{ entry.action }}</span>
        <span class="ml-auto text-xs font-mono" :class="entry.reward >= 0.5 ? 'text-accent-emerald' : 'text-accent-amber'">
          r={{ entry.reward?.toFixed(3) }}
        </span>
      </div>
      <p class="text-gray-300 text-xs leading-relaxed">{{ entry.summary }}</p>
      <p v-if="entry.drift > 0.05" class="text-accent-rose text-[10px] mt-1">
        KL drift: {{ entry.drift.toFixed(4) }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { watch, ref, nextTick } from 'vue'

const props = defineProps({
  log: { type: Array, default: () => [] },
})

const logContainer = ref(null)

watch(() => props.log.length, async () => {
  await nextTick()
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
})
</script>
