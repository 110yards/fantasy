<template>
  <v-container v-if="game && isPreGame">
    <p v-if="isPreGame" class="focus-game body-2">
      <label>Next game:</label>
      <span>{{ game.away_abbr.toUpperCase() }} @ {{ game.home_abbr.toUpperCase() }} - {{ gameDate }}</span>
    </p>
  </v-container>
  <v-container v-else-if="game">
    <p>
      <span class="team-icon" :class="game.away_abbr.toUpperCase()"> </span>
      <span class="focus-game body-2">{{ game.away_score }} &nbsp;&nbsp;&nbsp;{{ status }}</span>
    </p>
    <p class="mt-n2">
      <span class="team-icon pt-2" :class="game.home_abbr.toUpperCase()"> </span>
      <span class="focus-game body-2">{{ game.home_score }}</span>
    </p>
  </v-container>
</template>

<style scoped>
.focus-game {
  color: var(--color-secondary);
}

.game-state {
  color: white;
}
</style>

<script>
import scoreboard from "../../mixins/scoreboard"
import { shortDate, shortTime } from "../../modules/formatter"
export default {
  name: "focusgame",

  mixins: [scoreboard],
  computed: {
    game() {
      return this.scoreboard != null ? this.scoreboard.focus_game : null
    },
    isPreGame() {
      return this.game && this.game.game_date.toDate() > new Date()
    },
    isFinal() {
      return this.game && this.game.status === "complete"
    },
    gameDate() {
      if (this.isPreGame)
        return `${shortDate(this.game.game_date.toDate())}, ${shortTime(this.game.game_date.toDate())}`
    },
    status() {
      return this.isFinal ? "Final" : `${this.game.quarter} ${this.game.clock}`
    },
  },
}
</script>
