<template>
  <div>
    <v-row>
      <v-col class="pb-0 caption roster-name" :class="teamClass">
        <span v-if="roster">
          <router-link :to="{ name: 'roster', params: { leagueId: leagueId, rosterId: roster.id } }">
            {{ roster.name }}
          </router-link>
        </span>
        <span v-else>TBD</span>
      </v-col>
    </v-row>

    <v-row>
      <v-col class="py-0 text-h4" :class="scoreClass">
        <score :score="scoreFor" />
      </v-col>
    </v-row>

    <v-row>
      <v-col class="py-0 grey--text">
        <score v-if="enableProjections" :score="projection" />
      </v-col>
    </v-row>

    <v-row v-if="showMatchupProgress">
      <v-col>
        <matchup-progress :roster="roster" :reverse="reverse" :leagueId="leagueId" :class="!reverse ? 'pr-1' : ''" />
      </v-col>
    </v-row>
  </div>
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
    opponent: { type: Object, required: false },
    reverse: { type: Boolean, required: false, default: false },
    enableProjections: { type: Boolean, required: false, default: false },
    isCurrentWeek: { type: Boolean, required: false, default: false },
    scoreFor: { type: Number, required: false },
    scoreAgainst: { type: Number, required: false },
    projection: { type: Number },
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
