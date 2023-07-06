<template>
  <td v-if="gameResult" class="text-no-wrap">
    <!-- <a :href="cflLink" target="_blank"> -->
    <span class="">{{ date }} </span>
    <span class="d-none d-md-inline pl-1">{{ result }} {{ homeAwayMarker }} {{ opponent }}</span>
    <span class="d-md-none">({{ letterResult }})</span>
    <!-- </a> -->
  </td>
  <td v-else></td>
</template>

<script>
import * as formatter from "../../../modules/formatter"

export default {
  props: {
    gameResult: { type: Object, required: true },
  },

  computed: {
    isHome() {
      return this.gameResult.was_home
    },
    scoreFor() {
      return this.gameResult.score_for
    },
    scoreAgainst() {
      return this.gameResult.score_against
    },

    letterResult() {
      return this.gameResult.result
    },

    date() {
      let d = Date.parse(this.gameResult.game_date.toDate())
      return formatter.shortDate(d)
    },

    result() {
      return `${this.letterResult} ${this.scoreFor}-${this.scoreAgainst}`
    },

    homeAwayMarker() {
      return this.isHome ? "v" : "@"
    },

    opponent() {
      return this.gameResult.opponent_abbr.toUpperCase()
    },
  },
}
</script>
