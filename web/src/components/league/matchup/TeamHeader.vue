<template>
  <div></div>
</template>

<script>
import Score from "../../Score.vue"
import RosterScore from "../RosterScore.vue"
import MatchupProgress from "./MatchupProgress.vue"

export default {
  components: { Score, MatchupProgress, RosterScore },
  name: "TeamHeader",
  props: {
    leagueId: { type: String, required: true },
    roster: { type: Object, required: false },
    reverse: { type: Boolean, required: false, default: false },
    enableProjections: { type: Boolean, required: false, default: false },
    isCurrentWeek: { type: Boolean, required: false, default: false },
    scoreFor: { type: Number, required: false },
    scoreAgainst: { type: Number, required: false },
    projection: { type: Number },
    weekNumber: { type: Number, required: true },
  },

  computed: {
    currentUser() {
      return this.$store.state.currentUser
    },

    showMatchupProgress() {
      return this.isCurrentWeek && this.$root.enableMatchupProgress && this.roster
    },

    winningOrTied() {
      if (!this.scoreFor || !this.scoreAgainst) return null

      let winning = this.scoreFor > this.scoreAgainst
      let tied = this.scoreFor == this.scoreAgainst

      return winning || tied
    },

    scoreClass() {
      return this.winningOrTied ? null : "grey--text"
    },

    teamClass() {
      return this.winningOrTied ? "font-weight-black" : null
    },
  },
}
</script>
