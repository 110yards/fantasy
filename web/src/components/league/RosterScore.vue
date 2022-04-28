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
    calculatedScore: { type: Number, required: true },
  },
  data() {
    return {
      players: {},
      liveScore: 0.0,
    }
  },

  computed: {
    scoring() {
      return this.$root.leagueScoringSettings
    },

    score() {
      return this.isCurrentWeek ? this.liveScore : this.calculatedScore
    },

    isCurrentWeek() {
      return this.weekNumber == this.$root.state.current_week
    },
  },

  methods: {
    configureBindings() {
      if (!this.isCurrentWeek) return

      let season = this.$root.currentSeason

      let positions = Object.values(this.roster.positions)
      console.log(positions)

      let activePlayers = positions
        .filter(x => x.player && this.$root.isActivePositionType(x.position_type))
        .map(x => x.player)

      console.log(activePlayers)

      let playerIds = activePlayers.map(x => x.id)

      for (let playerId of playerIds) {
        // add each player id as an observable property on dataProp.players
        this.$set(this.players, playerId, null)
        // finally, bind to each player id property
        this.$bind(`players.${playerId}`, getPlayerGameRef(season, this.weekNumber, playerId))
      }
    },

    recalculateRosterScore() {
      if (!this.isCurrentWeek || !this.scoring || !this.roster) return
      let totalScore = 0.0

      if (!this.players) return totalScore

      let playerGameArrays = Object.values(this.players)

      let calcDetails = {
        roster: this.roster.name,
        scores: [],
      }

      for (let playerGameArray of playerGameArrays) {
        if (playerGameArray.length == 0) continue

        let game = playerGameArray[0]
        let gameScore = calculate(this.scoring, game.stats)
        calcDetails.scores.push({
          game: game.game_id,
          player: game.player_id,
          score: gameScore,
        })

        totalScore += gameScore
      }

      console.debug(calcDetails)

      this.liveScore = totalScore
    },
  },

  watch: {
    roster: {
      immediate: true,
      async handler(roster) {
        if (roster) {
          this.configureBindings()
          this.recalculateRosterScore()
        }
      },
    },

    scoring: {
      immediate: true,
      handler(scoring) {
        this.recalculateRosterScore()
      },
    },

    players: {
      deep: true,
      handler(players) {
        this.recalculateRosterScore()
        this.$emit("update", { score: this.liveScore })
      },
    },
  },
}
</script>
