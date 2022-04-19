<template>
  <div v-if="league">
    <league-header class="mb-n16" :leagueName="league.name" :leagueId="league.id" />
    <v-row>
      <v-col cols="12" md="8">
        <start-draft :league="league" />

        <app-primary-button v-if="canRenewLeague" @click="renewLeague"
          >Start {{ currentSeason }} Season</app-primary-button
        >

        <schedule v-if="scheduleGenerated && !isOffseason" :leagueId="leagueId" />

        <standings class="mt-5" v-if="!isOffseason" :league="league" />
        <transactions class="mt-5" v-if="!isOffseason" :leagueId="leagueId" />

        <season-summary :leagueId="leagueId" v-if="isOffseason" :season="league.season" />

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
import SeasonSummary from "../../components/league/SeasonSummary.vue"
import AppPrimaryButton from "../../components/buttons/AppPrimaryButton.vue"
import { renewLeague } from "../../api/110yards/league"
import SeasonList from "../../components/league/SeasonList.vue"
import LeagueHeader from "../../components/league/LeagueHeader.vue"

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
    SeasonSummary,
    AppPrimaryButton,
    SeasonList,
    LeagueHeader,
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
      return (this.$root.state && this.$root.state.is_offseason) || this.isPreviousSeason
    },

    leagueSeason() {
      if (!this.league) return null

      return this.league.season || 2021 // in the future, all leagues will have this set.
    },

    isPreviousSeason() {
      if (!this.league) return false

      return this.leagueSeason != this.currentSeason
    },

    currentSeason() {
      return this.$root.state.current_season
    },

    currentUserId() {
      return this.$store.state.uid
    },

    canRenewLeague() {
      return this.isPreviousSeason && this.league.commissioner_id == this.currentUserId
    },
  },

  methods: {
    async renewLeague() {
      await renewLeague(this.league.id)
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
