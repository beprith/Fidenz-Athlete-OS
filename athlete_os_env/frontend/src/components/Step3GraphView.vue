<template>
  <div class="card">
    <h2 class="text-xl font-semibold mb-4">Step 3 — Knowledge Graph</h2>
    <p class="text-gray-400 text-sm mb-4">
      Interactive force-directed graph showing Player, Team, League, Skill, and Match relationships.
    </p>

    <div class="bg-surface-900 rounded-lg border border-surface-600 mb-4" style="height: 500px">
      <div ref="graphContainer" class="w-full h-full"></div>
    </div>

    <!-- Legend -->
    <div class="flex flex-wrap gap-4 mb-6 text-xs">
      <span v-for="(color, type) in entityColors" :key="type" class="flex items-center gap-1.5">
        <span class="w-3 h-3 rounded-full" :style="{ background: color }"></span>
        {{ type }}
      </span>
    </div>

    <div class="flex justify-end">
      <button class="btn-primary" @click="$emit('next')">Continue to Simulation</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as d3 from 'd3'
import { getGraph } from '../api/simulation.js'

const emit = defineEmits(['next'])
const graphContainer = ref(null)
let simulation = null

const entityColors = {
  Player: '#06b6d4',
  Team: '#10b981',
  League: '#f59e0b',
  Skill: '#8b5cf6',
  Injury: '#f43f5e',
  Match: '#64748b',
  EpisodeMemory: '#94a3b8',
  Formation: '#fb923c',
}

onMounted(async () => {
  let data
  try {
    data = await getGraph()
  } catch {
    data = { nodes: [], edges: [] }
  }
  if (data.nodes.length) {
    renderGraph(data)
  }
})

onUnmounted(() => {
  if (simulation) simulation.stop()
})

function renderGraph(data) {
  const el = graphContainer.value
  if (!el) return

  const width = el.clientWidth
  const height = el.clientHeight || 500

  d3.select(el).selectAll('*').remove()

  const svg = d3.select(el)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', [0, 0, width, height])

  const g = svg.append('g')

  svg.call(d3.zoom().scaleExtent([0.2, 5]).on('zoom', (event) => {
    g.attr('transform', event.transform)
  }))

  const links = data.edges.map((e) => ({ source: e.source, target: e.target, relation: e.relation }))
  const nodeIds = new Set(data.nodes.map((n) => n.id))
  const validLinks = links.filter((l) => nodeIds.has(l.source) && nodeIds.has(l.target))

  simulation = d3.forceSimulation(data.nodes)
    .force('link', d3.forceLink(validLinks).id((d) => d.id).distance(80))
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(width / 2, height / 2))

  const link = g.append('g')
    .selectAll('line')
    .data(validLinks)
    .join('line')
    .attr('stroke', '#374151')
    .attr('stroke-width', 1)

  const node = g.append('g')
    .selectAll('circle')
    .data(data.nodes)
    .join('circle')
    .attr('r', (d) => d.type === 'Player' ? 10 : 6)
    .attr('fill', (d) => entityColors[d.type] || '#6b7280')
    .attr('stroke', '#1f2937')
    .attr('stroke-width', 1.5)
    .call(d3.drag()
      .on('start', (event, d) => {
        if (!event.active) simulation.alphaTarget(0.3).restart()
        d.fx = d.x; d.fy = d.y
      })
      .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y })
      .on('end', (event, d) => {
        if (!event.active) simulation.alphaTarget(0)
        d.fx = null; d.fy = null
      }))

  const label = g.append('g')
    .selectAll('text')
    .data(data.nodes.filter((n) => ['Player', 'Team', 'League'].includes(n.type)))
    .join('text')
    .text((d) => d.label || d.id)
    .attr('font-size', 10)
    .attr('fill', '#d1d5db')
    .attr('dx', 14)
    .attr('dy', 4)

  node.append('title').text((d) => `${d.type}: ${d.label || d.id}`)

  simulation.on('tick', () => {
    link
      .attr('x1', (d) => d.source.x).attr('y1', (d) => d.source.y)
      .attr('x2', (d) => d.target.x).attr('y2', (d) => d.target.y)
    node.attr('cx', (d) => d.x).attr('cy', (d) => d.y)
    label.attr('x', (d) => d.x).attr('y', (d) => d.y)
  })
}
</script>
