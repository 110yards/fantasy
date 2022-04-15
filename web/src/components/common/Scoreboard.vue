<template>
  <v-container v-if="games">
    <table class="scoreboard">
      <tbody v-for="game in games" :key="game.id" class="score">
        <tr class="away">
          <td class="team" :class="awayClass(game)">{{ game.teams.away.abbreviation }}</td>
          <td class="pts" :class="awayClass(game)">{{ game.score.away }}</td>
          <td class="caption">{{ gameStatus(game) }}</td>
        </tr>

        <tr class="home">
          <td class="team" :class="homeClass(game)">{{ game.teams.home.abbreviation }}</td>
          <td class="pts" :class="homeClass(game)">{{ game.score.home }}</td>
          <td class="caption">{{ gameStatusLine2(game) }}</td>
        </tr>
      </tbody>
    </table>
  </v-container>
</template>

<style scoped>
.scoreboard {
  float: right;
  color: var(--text-color);
}

.score .away td {
  padding-top: 1em;
}

.score .home td {
  border-bottom: 1px solid var(--bg-color-secondary);
  padding-bottom: 1em;
}

.score:last-child .home td {
  border-bottom: none;
}

.score .pts {
  text-align: right;
  border-right: 1px solid var(--bg-color-secondary);
  padding-right: 1em;
}

.score .team {
  width: 8em;
}

.score .won {
  font-weight: 500;
}

.score .caption {
  padding-left: 1em;
  padding-right: 1em;
}
</style>

<script>
import { eventStatus } from "../../api/110yards/constants"
import scoreboard from "../../mixins/scoreboard"
import { shortDate, shortTime } from "../../modules/formatter"
export default {
  name: "scoreboard",

  mixins: [scoreboard],
  computed: {
    games() {
      return this.scoreboard != null ? Object.values(this.scoreboard.games) : null
    },
  },

  methods: {
    awayClass(game) {
      let awayWon = game.event_status.event_status_id == eventStatus.Final && game.score.away >= game.score.home

      return awayWon ? "won" : ""
    },

    homeClass(game) {
      let homeWon = game.event_status.event_status_id == eventStatus.Final && game.score.home >= game.score.away

      return homeWon ? "won" : ""
    },

    gameStatus(game) {
      switch (game.event_status.event_status_id) {
        case eventStatus.PreGame:
          return `${shortDate(game.date_start.toDate())}`

        case eventStatus.Cancelled:
          return "Cancelled"

        case eventStatus.Postponed:
          return "Postponed"

        case eventStatus.Final:
          return "Final"

        default:
          return `${this.formatQuarter(game.event_status.quarter)}`
      }
    },

    formatQuarter(quarter) {
      switch (quarter) {
        case 1:
          return "Q1"
        case 2:
          return "Q2"
        case 3:
          return "Q3"
        case 4:
          return "Q4"
        default:
          return "OT"
      }
    },

    gameStatusLine2(game) {
      switch (game.event_status.event_status_id) {
        case eventStatus.PreGame:
          return `${shortTime(game.date_start.toDate())}`

        case eventStatus.InProgress:
          return `${game.event_status.minutes}:${String(game.event_status.seconds).padStart(2, "0")}`

        default:
          return ""
      }
    },
  },
}
</script>
