import { defineStore } from 'pinia'

export const useSimulationStore = defineStore('simulation', {
  state: () => ({
    status: 'idle',
    scenarioA: { team: '', rounds: [], summary: '', elapsed: 0 },
    scenarioB: { team: '', rounds: [], summary: '', elapsed: 0 },
    roundEvents: [],
    agentStatuses: {},
    graphData: { nodes: [], edges: [] },
    currentStep: 0,
    activePhase: 1,
    phases: [
      { id: 1, name: 'Data Ingest', status: 'pending' },
      { id: 2, name: 'Persona Forge', status: 'pending' },
      { id: 3, name: 'Graph Build', status: 'pending' },
      { id: 4, name: 'Simulation', status: 'pending' },
      { id: 5, name: 'Report', status: 'pending' },
    ],
  }),

  getters: {
    currentPhase: (state) => state.phases.find((p) => p.id === state.activePhase),
    completedPhases: (state) => state.phases.filter((p) => p.status === 'done').length,
  },

  actions: {
    setPhase(phaseId) {
      this.activePhase = phaseId
      this.phases.forEach((p) => {
        if (p.id < phaseId) p.status = 'done'
        else if (p.id === phaseId) p.status = 'active'
        else p.status = 'pending'
      })
    },

    addRoundEvent(event) {
      this.roundEvents.push({
        ...event,
        timestamp: Date.now(),
      })
      if (this.roundEvents.length > 200) {
        this.roundEvents = this.roundEvents.slice(-100)
      }
    },

    updateAgentStatus(agentId, status) {
      this.agentStatuses[agentId] = status
    },

    setGraphData(data) {
      this.graphData = data
    },

    updateScenario(scenario, data) {
      if (scenario === 'a') Object.assign(this.scenarioA, data)
      else Object.assign(this.scenarioB, data)
    },

    resetSim() {
      this.status = 'idle'
      this.scenarioA = { team: '', rounds: [], summary: '', elapsed: 0 }
      this.scenarioB = { team: '', rounds: [], summary: '', elapsed: 0 }
      this.roundEvents = []
      this.agentStatuses = {}
      this.currentStep = 0
      this.activePhase = 1
      this.phases.forEach((p) => { p.status = 'pending' })
    },

    handleWsEvent(event) {
      switch (event.type) {
        case 'agent_status':
          this.updateAgentStatus(event.agent_id, event.status)
          break
        case 'round_event':
          this.addRoundEvent(event)
          break
        case 'graph_update':
          if (event.node) this.graphData.nodes.push(event.node)
          if (event.edge) this.graphData.edges.push(event.edge)
          break
        case 'phase_change':
          this.status = event.phase
          break
        case 'drift_alert':
          this.addRoundEvent({ type: 'drift_alert', ...event })
          break
      }
    },
  },
})
