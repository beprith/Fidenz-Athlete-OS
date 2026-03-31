<template>
  <div class="card">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold">Step 5 — Scouting Report</h2>
      <div class="flex gap-2">
        <button class="btn-secondary text-sm" @click="fetchReport" :disabled="loading">
          {{ loading ? 'Generating...' : 'Generate Report' }}
        </button>
      </div>
    </div>

    <div v-if="grade > 0" class="mb-6 flex items-center gap-4">
      <div class="text-3xl font-extrabold" :class="gradeColor">{{ (grade * 100).toFixed(0) }}%</div>
      <div>
        <p class="text-sm text-gray-400">Overall Grade</p>
        <p class="text-sm" :class="gradeColor">{{ gradeLabel }}</p>
      </div>
    </div>

    <div v-if="reportHtml" class="prose prose-invert prose-sm max-w-none" v-html="reportHtml"></div>

    <div v-else class="text-gray-500 text-sm py-8 text-center">
      Complete the simulation to generate a scouting report.
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { marked } from 'marked'
import { getReport } from '../api/simulation.js'

const report = ref('')
const grade = ref(0)
const loading = ref(false)

const reportHtml = computed(() => {
  if (!report.value) return ''
  return marked.parse(report.value)
})

const gradeColor = computed(() => {
  if (grade.value >= 0.7) return 'text-accent-emerald'
  if (grade.value >= 0.4) return 'text-accent-amber'
  return 'text-accent-rose'
})

const gradeLabel = computed(() => {
  if (grade.value >= 0.7) return 'Recommended'
  if (grade.value >= 0.4) return 'Further Evaluation'
  return 'Not Recommended'
})

async function fetchReport() {
  loading.value = true
  try {
    const data = await getReport()
    report.value = data.report
    grade.value = data.grade
  } catch (err) {
    report.value = '**Error generating report.** Please ensure a simulation has been run first.'
  } finally {
    loading.value = false
  }
}
</script>
