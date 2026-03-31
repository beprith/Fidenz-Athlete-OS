<template>
  <div>
    <canvas ref="chartCanvas" height="200"></canvas>
    <div v-if="!rewards.length" class="text-gray-500 text-sm text-center py-8">
      No reward data yet. Run a simulation step.
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({
  rewards: { type: Array, default: () => [] },
  kl: { type: Array, default: () => [] },
})

const chartCanvas = ref(null)
let chart = null

function buildChart() {
  if (!chartCanvas.value) return
  if (chart) chart.destroy()

  const labels = props.rewards.map((_, i) => i + 1)

  chart = new Chart(chartCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Reward',
          data: props.rewards,
          borderColor: '#06b6d4',
          backgroundColor: 'rgba(6, 182, 212, 0.1)',
          fill: true,
          tension: 0.3,
          pointRadius: 2,
        },
        {
          label: 'KL Penalty',
          data: props.kl,
          borderColor: '#f43f5e',
          backgroundColor: 'rgba(244, 63, 94, 0.1)',
          fill: true,
          tension: 0.3,
          pointRadius: 2,
        },
        {
          label: 'Net',
          data: props.rewards.map((r, i) => Math.max(0, r - (props.kl[i] || 0))),
          borderColor: '#10b981',
          borderDash: [4, 4],
          tension: 0.3,
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: '#1f2937' }, ticks: { color: '#6b7280', font: { size: 10 } } },
        y: { grid: { color: '#1f2937' }, ticks: { color: '#6b7280', font: { size: 10 } }, min: 0, max: 1 },
      },
      plugins: {
        legend: { labels: { color: '#9ca3af', font: { size: 11 } } },
      },
    },
  })
}

onMounted(buildChart)
onUnmounted(() => { if (chart) chart.destroy() })

watch([() => props.rewards.length, () => props.kl.length], buildChart)
</script>
