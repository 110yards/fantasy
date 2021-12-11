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
    scoring: { type: Object, required: false },
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

    recalculateRosterScore() {
      let totalScore = 0.0

      if (!this.players) return totalScore

      let scoring = this.scoring || this.$root.leagueScoringSettings

      let playerGameArrays = Object.values(this.players)

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

    scoring: {
      immediate: true,
      handler(scoring) {
        if (scoring) this.score = this.recalculateRosterScore()
      },
    },

    players: {
      deep: true,
      handler(players) {
        this.score = this.recalculateRosterScore()
        this.$emit("update", { score: this.score })
      },
    },
  },
}
</script>
