import { defineStore } from 'pinia'
import { getPlayers, getTeams } from '../api/simulation.js'

export const useSquadStore = defineStore('squad', {
  state: () => ({
    players: [],
    teams: [],
    selectedPlayers: [],
    chemistryMatrix: [],
    weakestLink: null,
    strongestPair: null,
    loading: false,
    error: null,
  }),

  getters: {
    playerMap: (state) => {
      const map = {}
      state.players.forEach((p) => { map[p.player_id] = p })
      return map
    },
    selectedCount: (state) => state.selectedPlayers.length,
  },

  actions: {
    async fetchPlayers() {
      this.loading = true
      try {
        this.players = await getPlayers()
      } catch (err) {
        this.error = err.message
      } finally {
        this.loading = false
      }
    },

    async fetchTeams() {
      try {
        this.teams = await getTeams()
      } catch (err) {
        this.error = err.message
      }
    },

    togglePlayer(playerId) {
      const idx = this.selectedPlayers.indexOf(playerId)
      if (idx >= 0) {
        this.selectedPlayers.splice(idx, 1)
      } else {
        this.selectedPlayers.push(playerId)
      }
    },

    setChemistryMatrix(matrix) {
      this.chemistryMatrix = matrix
      this._computeExtremes()
    },

    _computeExtremes() {
      const n = this.chemistryMatrix.length
      if (n < 2) return

      let minScore = Infinity, maxScore = -Infinity
      let minPair = null, maxPair = null

      for (let i = 0; i < n; i++) {
        for (let j = i + 1; j < n; j++) {
          const s = this.chemistryMatrix[i]?.[j] ?? 0
          if (s < minScore) { minScore = s; minPair = [i, j] }
          if (s > maxScore) { maxScore = s; maxPair = [i, j] }
        }
      }

      this.weakestLink = minPair ? {
        players: minPair.map((i) => this.selectedPlayers[i]),
        score: minScore,
      } : null

      this.strongestPair = maxPair ? {
        players: maxPair.map((i) => this.selectedPlayers[i]),
        score: maxScore,
      } : null
    },
  },
})
