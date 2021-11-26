<template>
  <div v-if="league">
    <league-menu :league="league" />
    <v-row>
      <v-col cols="12" md="8">
        <h4 class="brand">{{ league.name }}</h4>
        <start-draft :league="league" />

        <schedule v-if="scheduleGenerated && !isOffseason" :leagueId="leagueId" />

        <standings class="mt-5" v-if="!isOffseason" :league="league" />
        <transactions class="mt-5" v-if="!isOffseason" :leagueId="leagueId" />

        <season-summary :leagueId="leagueId" v-if="isOffseason" />

        <!-- @*@Html.Partial("CflNews", Model.News)*@ -->
      </v-col>

      <v-col cols="4" class="d-none d-md-flex">
        <scoreboard />
      </v-col>
    </v-row>
  </div>
</template>

<style scoped>
.carousel-control-icon {
  height: 0.8em;
}
.v-icon.commissioner {
  color: yellow;
  font-size: 0.9em;
}
</style>

<script>
import { firestore } from "../../modules/firebase"
import StartDraft from "../../components/commissioner/StartDraft"
import MatchupPreview from "../../components/league/MatchupPreview"
import Schedule from "../../components/league/Schedule.vue"
import Standings from "../../components/league/Standings.vue"
import Transactions from "../../components/league/Transactions.vue"
import Scoreboard from "../../components/common/Scoreboard.vue"
import LeagueMenu from "../../components/league/LeagueMenu.vue"
import SeasonSummary from "../../components/league/SeasonSummary.vue"

export default {
  name: "league-index",
  props: ["leagueId"],
  components: {
    StartDraft,
    MatchupPreview,
    Schedule,
    Standings,
    Transactions,
    Scoreboard,
    LeagueMenu,
    SeasonSummary,
  },
  data() {
    return {
      league: null,
      rosters: [],
      weeks: [],
    }
  },
  computed: {
    isCommissioner() {
      if (this.league == null || this.$store.state.currentUser == null) return false

      return this.league.commissioner_id == this.$store.state.currentUser.uid
    },

    scheduleGenerated() {
      return this.league && this.league.schedule_generated
    },

    isOffseason() {
      return this.$root.state && this.$root.state.is_offseason
    },
  },

  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        if (leagueId == null) return

        this.$bind("league", firestore.collection("league").doc(leagueId))
      },
    },
  },
}
</script>
