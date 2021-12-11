<template>
  <score :score="score" />
</template>

<script>
import { calculate, getPlayerGameRef } from "../../modules/scoring"
import Score from "../Score.vue"

export default {
  components: { Score },
  props: {
    roster: { type: Object, required: false },
    weekNumber: { required: true },
  },
  data() {
    return {
      players: {},
      score: 0.0,
    }
  },

  methods: {
    configureBindings() {
      let season = this.$root.currentSeason

      let positions = Object.values(this.roster.positions)
      let players = positions.filter(x => x.player).map(x => x.player)
      let playerIds = players.map(x => x.id)

      for (let playerId of playerIds) {
        // add each player id as an observable property on dataProp.players
        this.$set(this.players, playerId, null)
        // finally, bind to each player id property
        this.$bind(`players.${playerId}`, getPlayerGameRef(season, this.weekNumber, playerId))
      }
    },

    calculateRosterScore(scoring, playerGames) {
      let totalScore = 0.0

      if (!playerGames) return totalScore

      let playerGameArrays = Object.values(playerGames)

      for (let playerGameArray of playerGameArrays) {
        if (playerGameArray.length == 0) continue

        let game = playerGameArray[0]
        totalScore += calculate(scoring, game.stats)
      }

      return totalScore
    },
  },

  watch: {
    roster: {
      immediate: true,
      async handler(roster) {
        if (roster) {
          this.configureBindings()
        }
      },
    },

    players: {
      deep: true,
      handler(players) {
        this.score = this.calculateRosterScore(this.$root.leagueScoringSettings, players)
        this.$emit("update", { score: this.score })
      },
    },
  },
}
</script>
