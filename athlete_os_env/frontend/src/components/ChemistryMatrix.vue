<template>
  <div class="overflow-x-auto">
    <table class="border-collapse">
      <thead>
        <tr>
          <th class="w-20"></th>
          <th
            v-for="p in players"
            :key="p.player_id"
            class="text-xs text-gray-400 font-medium px-1 py-1 -rotate-45 origin-bottom-left w-10"
          >
            {{ shortName(p.name) }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, i) in matrix" :key="i">
          <td class="text-xs text-gray-400 font-medium pr-2 text-right">{{ shortName(players[i]?.name) }}</td>
          <td
            v-for="(score, j) in row"
            :key="j"
            class="w-10 h-10 text-center text-[10px] font-mono border border-surface-700 cursor-default"
            :style="{ background: chemColor(score) }"
            :title="`${players[i]?.name} ↔ ${players[j]?.name}: ${score.toFixed(2)}`"
          >
            {{ i !== j ? score.toFixed(1) : '' }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  matrix: { type: Array, required: true },
  players: { type: Array, required: true },
})

function chemColor(score) {
  const r = Math.round(255 * (1 - score))
  const g = Math.round(255 * score)
  return `rgba(${r}, ${g}, 60, 0.6)`
}

function shortName(name) {
  if (!name) return ''
  const parts = name.split(' ')
  return parts.length > 1 ? parts[parts.length - 1] : name
}
</script>
