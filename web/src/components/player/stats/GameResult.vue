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
      return this.game.home.id == this.playerTeam.id
    },
    scoreFor() {
      return this.isHome ? this.game.home_score : this.game.away_score
    },
    scoreAgainst() {
      return this.isHome ? this.game.away_score : this.game.home_score
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
      let isHome = game.home.abbr == this.playerTeam.abbr
      let opponent = isHome ? game.away : game.home

      return isHome ? `v ${opponent.abbr}` : `@ ${opponent.abbr}`
    },
  },
}
</script>
