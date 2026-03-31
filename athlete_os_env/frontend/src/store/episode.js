import { defineStore } from 'pinia'
import { resetEnv, stepEnv, getState } from '../api/environment.js'

export const useEpisodeStore = defineStore('episode', {
  state: () => ({
    episodeId: '',
    taskId: '',
    goal: '',
    playerSummary: '',
    stepCount: 0,
    currentRound: 0,
    totalRounds: 0,
    cumulativeReward: 0,
    done: false,
    simulationStatus: 'idle',
    lastObservation: null,
    stepLog: [],
    rewardHistory: [],
    klHistory: [],
    loading: false,
    error: null,
  }),

  getters: {
    isActive: (state) => state.episodeId && !state.done,
    avgReward: (state) => {
      if (!state.rewardHistory.length) return 0
      return state.rewardHistory.reduce((a, b) => a + b, 0) / state.rewardHistory.length
    },
  },

  actions: {
    async reset(taskId = null) {
      this.loading = true
      this.error = null
      try {
        const result = await resetEnv(taskId)
        const obs = result.observation
        this.episodeId = Date.now().toString()
        this.taskId = taskId || 'single_player_stat_prediction'
        this.goal = obs.goal || ''
        this.playerSummary = obs.player_summary || ''
        this.stepCount = 0
        this.currentRound = 0
        this.cumulativeReward = 0
        this.done = false
        this.simulationStatus = 'idle'
        this.lastObservation = obs
        this.stepLog = []
        this.rewardHistory = []
        this.klHistory = []
      } catch (err) {
        this.error = err.message
      } finally {
        this.loading = false
      }
    },

    async step(action) {
      this.loading = true
      this.error = null
      try {
        const result = await stepEnv(action)
        const obs = result.observation
        this.stepCount++
        this.currentRound++
        this.cumulativeReward += result.reward || 0
        this.done = result.done
        this.lastObservation = obs
        this.playerSummary = obs.player_summary || this.playerSummary
        this.simulationStatus = this.done ? 'done' : 'simulating'

        this.rewardHistory.push(result.reward || 0)
        this.klHistory.push(obs.persona_drift_score || 0)
        this.stepLog.push({
          step: this.stepCount,
          reward: result.reward,
          drift: obs.persona_drift_score,
          action: action.action_type,
          summary: obs.player_summary,
        })

        return result
      } catch (err) {
        this.error = err.message
        return null
      } finally {
        this.loading = false
      }
    },

    async fetchState() {
      try {
        const state = await getState()
        this.simulationStatus = state.simulation_status || this.simulationStatus
        this.done = state.done || this.done
      } catch (err) {
        this.error = err.message
      }
    },

    updateFromWs(event) {
      if (event.type === 'reward_update') {
        this.rewardHistory.push(event.reward)
        this.klHistory.push(event.kl_penalty)
      }
      if (event.type === 'phase_change') {
        this.simulationStatus = event.phase
      }
    },
  },
})
