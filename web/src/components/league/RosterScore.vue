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
    calculatedScore: { type: Number, required: false, default: 0.0 },
    scoring: { type: Object, required: false },
  },
  data() {
    return {
      players: {},
      liveScore: 0.0,
    }
  },

  computed: {
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
      // console.log(positions)

      let activePlayers = positions
        .filter(x => x.player && this.$root.isActivePositionType(x.position_type) && !x.player.is_free_agent)
        .map(x => x.player)

      let teamGameIds = {}

      for (let player of activePlayers) {
        // add each player id as an observable property on dataProp.players
        this.$set(this.players, player.player_id, null)

        // check if player.team_abbr in teamGameIds
        if (!teamGameIds[player.team_abbr]) {
          // if not, get the game id for that team
          teamGameIds[player.team_abbr] = this.$root.getGameIdForTeam(player.team_abbr)
        }

        // finally, bind to each player id property
        if (!teamGameIds[player.team_abbr]) continue
        let ref = getPlayerGameRef(season, teamGameIds[player.team_abbr], player.player_id)

        this.$rtdbBind(`players.${player.player_id}`, ref)
      }
    },

    recalculateRosterScore() {
      if (!this.isCurrentWeek || !this.scoring || !this.roster) return
      let totalScore = 0.0

      if (!this.players) return totalScore

      let stats = Object.values(this.players)

      let calcDetails = {
        roster: this.roster.name,
        scores: [],
      }

      for (let playerStats of stats) {
        if (!playerStats) continue

        let gameScore = calculate(this.scoring, playerStats)
        calcDetails.scores.push({
          player: playerStats.player,
          score: gameScore,
        })

        totalScore += gameScore
      }

      // console.debug(calcDetails)

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
