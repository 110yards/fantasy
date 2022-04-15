<template>
  <td v-if="game && playerTeam" class="text-no-wrap">
    <a :href="cflLink" target="_blank">
      <span class="">{{ date }} </span>
      <span class="d-none d-md-inline pl-1">{{ result }} {{ opponent }}</span>
      <span class="d-md-none">({{ letterResult }})</span>
    </a>
  </td>
  <td v-else></td>
</template>

<script>
import * as formatter from "../../../modules/formatter"

export default {
  props: {
    playerTeam: { type: Object, required: true },
    game: { type: Object, required: true },
  },

  computed: {
    isHome() {
      return this.game.teams.home.id == this.playerTeam.id
    },
    scoreFor() {
      return this.isHome ? this.game.score.home : this.game.score.away
    },
    scoreAgainst() {
      return this.isHome ? this.game.score.away : this.game.score.home
    },

    letterResult() {
      let won = this.scoreFor > this.scoreAgainst
      let lost = this.scoreFor < this.scoreAgainst

      return won ? "W" : lost ? "L" : "T"
    },

    cflLink() {
      return `https://www.cfl.ca/games/${this.game.id}/#/boxscore`
    },
    date() {
      let d = Date.parse(this.game.date_start)
      return formatter.shortDate(d)
    },

    result() {
      return `${this.letterResult} ${this.scoreFor}-${this.scoreAgainst}`
    },

    opponent() {
      let game = this.game
      let isHome = game.teams.home.id == this.playerTeam.id
      let opponent = isHome ? game.teams.away : game.teams.home

      return isHome ? `v ${opponent.abbreviation}` : `@ ${opponent.abbreviation}`
    },
  },
}
</script>
