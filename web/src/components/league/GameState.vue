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
    scoreboard: { type: Object, required: true },
    short: { type: Boolean, required: false, default: false },
  },

  computed: {
    gameStatus() {
      if (!this.player) return null
      if (this.player.team.abbr == "FA") return "No game"

      let game = this.$root.getGameForTeam(this.player.team.abbr, this.scoreboard)

      if (!game) return "Bye week"

      let isHomePlayer = game.home.abbr == this.player.team.abbr
      let vsMarker = isHomePlayer ? "v" : "@"
      let scoreFor = isHomePlayer ? game.home_score : game.away_score
      let scoreAgainst = isHomePlayer ? game.away_score : game.home_score
      let opponent = this.$root.getOpponent(this.player.team.abbr)

      switch (game.game_status.status_id) {
        case eventStatus.PreGame: {
          let date = game.date_start.toDate()
          let start = formatter.gameStartTime(date, this.short)
          return `${start} ${vsMarker} ${opponent}`
        }

        case eventStatus.InProgress:
          return `Q${game.game_status.quarter} ${scoreFor}-${scoreAgainst} ${vsMarker} ${opponent}`

        case eventStatus.Final: {
          let won = scoreFor > scoreAgainst
          let lost = scoreFor < scoreAgainst
          let result = won ? "W" : lost ? "L" : "T"
          return `Final ${result} ${scoreFor}-${scoreAgainst} ${vsMarker} ${opponent}`
        }
        case eventStatus.Postponed:
          return game.event_status.name

        default:
          return `${vsMarker} ${opponent} - ${game.game_status.name}`
      }
    },
  },
}
</script>
