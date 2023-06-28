<template>
  <span>
    {{ gameStatus }}
  </span>
</template>

<script>
import { eventStatus } from "../../api/110yards/constants"
import * as formatter from "../../modules/formatter"

export default {
  name: "GameState",
  props: {
    player: {
      type: Object,
      required: false,
    },
    short: { type: Boolean, required: false, default: false },
  },

  computed: {
    gameStatus() {
      if (!this.player || !this.$root.scoreboard) return null
      if (this.player.team_abbr == "FA") return "No game"

      let team = this.$root.scoreboard.teams[this.player.team_abbr]

      if (!team.game) return "Bye week"

      let game = team.game

      let isHomePlayer = team.is_at_home
      let vsMarker = isHomePlayer ? "v" : "@"
      let scoreFor = isHomePlayer ? game.home_score : game.away_score
      let scoreAgainst = isHomePlayer ? game.away_score : game.home_score
      let opponent = team.opponent.toUpperCase()

      switch (game.status) {
        case eventStatus.PreGame: {
          let date = game.game_date.toDate()
          let start = formatter.gameStartTime(date, this.short)
          return `${start} ${vsMarker} ${opponent}`
        }

        case eventStatus.InProgress:
          return `${game.quarter} ${scoreFor}-${scoreAgainst} ${vsMarker} ${opponent}`

        case eventStatus.Final: {
          let won = scoreFor > scoreAgainst
          let lost = scoreFor < scoreAgainst
          let result = won ? "W" : lost ? "L" : "T"
          return `Final ${result} ${scoreFor}-${scoreAgainst} ${vsMarker} ${opponent}`
        }
        default:
          return `${vsMarker} ${opponent} - ${game.status}`
      }
    },
  },
}
</script>
