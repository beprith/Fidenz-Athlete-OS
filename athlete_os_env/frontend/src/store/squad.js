import { defineStore } from 'pinia'
import { getPlayers, getTeams, getCompatibleTeams } from '../api/simulation.js'

export const useSquadStore = defineStore('squad', {
  state: () => ({
    players: [],
    teams: [],
    compatibleTeams: [],
    selectedPlayerId: null,
    selectedTeam: null,
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
    selectedPlayer: (state) => {
      if (!state.selectedPlayerId) return null
      return state.players.find((p) => p.player_id === state.selectedPlayerId) || null
    },
    selectedPlayerSport: (state) => {
      if (!state.selectedPlayerId) return null
      const p = state.players.find((p) => p.player_id === state.selectedPlayerId)
      return p ? p.sport : null
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

    async selectPlayer(playerId) {
      this.selectedPlayerId = playerId
      this.selectedTeam = null
      this.compatibleTeams = []
      if (playerId) {
        try {
          const result = await getCompatibleTeams(playerId)
          this.compatibleTeams = result.teams
        } catch (err) {
          this.error = err.message
          this.compatibleTeams = this.teams
        }
      }
    },

    selectTeam(team) {
      this.selectedTeam = team
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
