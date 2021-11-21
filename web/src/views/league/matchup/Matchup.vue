<template>
  <v-sheet v-if="league && matchup">
    <v-row class="heading mb-2 text-right">
      <v-col cols="5" class="roster-name pl-4">
        <team-header
          :leagueId="leagueId"
          :roster="awayRoster"
          :opponent="homeRoster"
          :reverse="true"
          :enableProjections="enableProjections"
          :isCurrentWeek="isCurrentWeek"
          :scoreFor="awayScore"
          :scoreAgainst="homeScore"
          :projection="awayProjection"
        />
      </v-col>

      <v-col cols="2" class="text-center">
        <v-row>
          <v-col class="pb-0">vs</v-col>
        </v-row>
      </v-col>

      <v-col cols="5" class="roster-name pr-4 text-left">
        <team-header
          :leagueId="leagueId"
          :roster="homeRoster"
          :opponent="awayRoster"
          :enableProjections="enableProjections"
          :isCurrentWeek="isCurrentWeek"
          :scoreFor="homeScore"
          :scoreAgainst="awayScore"
          :projection="homeProjection"
        />
      </v-col>
    </v-row>

    <matchup-vs
      class="d-none d-md-block"
      :league="league"
      :away="awayRoster"
      :home="homeRoster"
      :enableProjections="enableProjections"
      :weekNumber="weekNumber"
    />
    <matchup-vs
      class="d-md-none"
      mobile
      :league="league"
      :away="awayRoster"
      :home="homeRoster"
      :enableProjections="enableProjections"
      :weekNumber="weekNumber"
    />
  </v-sheet>
</template>

<style scoped>
.heading {
  border-bottom: 1px solid black;
}

.active {
  font-weight: bold;
}
</style>

<script>
import { firestore } from "../../../modules/firebase"
import { matchupType } from "../../../api/110yards/constants"
import MatchupVs from "../../../components/league/matchup/MatchupVs.vue"
import TeamHeader from "../../../components/league/matchup/TeamHeader.vue"
import { rosterScore } from "../../../api/110yards/score"
import scoreboard from "../../../mixins/scoreboard"

export default {
  name: "matchup",
  components: {
    MatchupVs,
    TeamHeader,
  },
  mixins: [scoreboard],
  props: {
    leagueId: {
      type: String,
      required: true,
    },
    weekNumber: {
      required: true,
    },
    matchupId: {
      required: true,
    },
  },
  data() {
    return {
      matchup: null,
      awayRoster: null,
      homeRoster: null,
      league: null,
      awayScore: null,
      homeScore: null,
      awayProjection: null,
      homeProjection: null,
    }
  },
  computed: {
    enableProjections() {
      return this.isCurrentWeek && this.$root.enableProjections
    },

    isCurrentWeek() {
      return this.weekNumber == this.$root.state.current_week
    },

    title() {
      if (!this.matchup) return null

      return this.matchup.type == matchupType.Regular ? `Week ${this.weekNumber}` : this.matchup.type_display
    },

    includeProjection() {
      return true
    },
  },
  methods: {
    configureLeagueReference() {
      if (!this.leagueId) return

      let ref = firestore.collection("league").doc(this.leagueId)
      this.$bind("league", ref)
    },

    configureMatchupReference() {
      if (!this.leagueId || !this.weekNumber || !this.matchupId) return

      let path = `league/${this.leagueId}/week/${this.weekNumber}/matchup/${this.matchupId}`
      let ref = firestore.doc(path)

      this.$bind("matchup", ref)
    },

    configureRosterReferences() {
      if (!this.matchup || !this.matchup.away || !this.matchup.home) return

      let leagueRef = firestore.doc(`league/${this.leagueId}`)
      this.$bind("league", leagueRef)

      if (this.isCurrentWeek) {
        let rostersRef = firestore.collection(`league/${this.leagueId}/roster`)
        let awayRef = rostersRef.doc(this.matchup.away.id)
        let homeRef = rostersRef.doc(this.matchup.home.id)

        this.$bind("awayRoster", awayRef)
        this.$bind("homeRoster", homeRef)
      } else {
        this.awayRoster = this.matchup.away
        this.homeRoster = this.matchup.home
      }
    },

    async updateHomeScores() {
      if (this.homeRoster && this.isCurrentWeek && this.scoreboard) {
        let homeResult = await rosterScore(this.leagueId, this.homeRoster.id)
        this.homeScore = homeResult.score
        this.homeProjection = homeResult.projection
      } else {
        this.homeScore = this.matchup.home_score
      }
    },

    async updateAwayScores() {
      if (this.awayRoster && this.isCurrentWeek && this.scoreboard) {
        let awayResult = await rosterScore(this.leagueId, this.awayRoster.id)
        this.awayScore = awayResult.score
        this.awayProjection = awayResult.projection
      } else {
        this.awayScore = this.matchup.away_score
      }
    },
  },
  watch: {
    matchupId: {
      immediate: true,
      handler(matchupId) {
        this.configureMatchupReference()
      },
    },
    leagueId: {
      immediate: true,
      handler(leagueId) {
        this.configureLeagueReference()
        this.configureMatchupReference()
      },
    },
    weekNumber: {
      immediate: true,
      handler(weekNumber) {
        this.configureMatchupReference()
      },
    },
    matchup: {
      handler(matchup) {
        this.configureRosterReferences()
      },
    },

    awayRoster: {
      async handler(awayRoster) {
        this.updateAwayScores()
      },
    },

    homeRoster: {
      handler(homeRoster) {
        this.updateHomeScores()
      },
    },

    scoreboard: {
      handler(scoreboard) {
        this.updateHomeScores()
        this.updateAwayScores()
      },
    },
  },
}
</script>
