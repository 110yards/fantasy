<template>
  <v-container v-if="games">
    <table class="scoreboard">
      <tbody v-for="game in games" :key="game.id" class="score">
        <tr class="away">
          <td class="team" :class="awayClass(game)">{{ game.away_abbr.toUpperCase() }}</td>
          <td class="pts" :class="awayClass(game)">{{ game.away_score }}</td>
          <td class="caption">{{ gameStatus(game) }}</td>
        </tr>

        <tr class="home">
          <td class="team" :class="homeClass(game)">{{ game.home_abbr.toUpperCase() }}</td>
          <td class="pts" :class="homeClass(game)">{{ game.home_score }}</td>
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
    isPreGame(game) {
      return game.game_date > new Date()
    },

    isFinal(game) {
      return game.status == "complete"
    },
    awayClass(game) {
      let awayWon = this.isFinal(game) && game.away_score >= game.home_score

      return awayWon ? "won" : ""
    },

    homeClass(game) {
      let homeWon = this.isFinal(game) && game.home_score >= game.away_score

      return homeWon ? "won" : ""
    },

    gameStatus(game) {
      if (this.isPreGame(game)) {
        return `${shortDate(game.game_date.toDate())}`
      }

      if (game.status == "complete") {
        return "Final"
      }

      // return `${this.formatQuarter(game.quarter)}`
      return game.quarter
    },

    // formatQuarter(quarter) {
    //   switch (quarter) {
    //     case "Q1":
    //       return "Q1"
    //     case "2":
    //       return "Q2"
    //     case "3":
    //       return "Q3"
    //     case "4":
    //       return "Q4"
    //     default:
    //       return "OT"
    //   }
    // },

    gameStatusLine2(game) {
      if (this.isPreGame(game)) {
        return `${shortTime(game.game_date.toDate())}`
      }

      if (this.isFinal(game)) {
        return ""
      }

      return `${game.clock}`
    },
  },
}
</script>
