<template>
  <div>
    <v-alert type="info" dense v-if="wasAdjusted" class="mb-10">
      <span>Scores for this matchup were adjusted by the commissioner.</span>
    </v-alert>

    <v-sheet v-if="league && matchup">
      <matchup-header
        :matchup="matchup"
        :away="awayRoster"
        :home="homeRoster"
        :weekNumber="weekNumber"
        :enableProjections="enableProjections"
        :isCurrentWeek="isCurrentWeek"
      />

      <matchup-vs
        class="d-none d-md-block"
        v-if="!editing"
        :league="league"
        :away="awayRoster"
        :home="homeRoster"
        :enableProjections="enableProjections"
        :weekNumber="weekNumber"
      />
      <matchup-vs
        class="d-md-none"
        mobile
        v-if="!editing"
        :league="league"
        :away="awayRoster"
        :home="homeRoster"
        :enableProjections="enableProjections"
        :weekNumber="weekNumber"
      />

      <!-- <v-row class="mt-2" v-if="canEdit && !editing">
        <v-col cols="12">
          <v-btn @click="startEditing">Edit scores</v-btn>
        </v-col>
      </v-row> -->
    </v-sheet>

    <v-sheet v-if="editing">
      <v-row>
        <v-col md="6" cols="12">
          <p class="subtitle-2">
            As the commissioner, you may apply an adjustment to either or both teams in order to correct an error.
            Results will be re-calculated when you save. Adjustments may be positive or negative.
          </p>
          <v-form ref="form" @submit.prevent="applyAdjustments()">
            <app-number-field v-model="form.away_adjustment" :label="awayRoster.name + ' adjustment'" required />

            <app-number-field v-model="form.home_adjustment" :label="homeRoster.name + ' adjustment'" required />

            <p class="body-1">Adjusted scores</p>
            <p class="body-2">{{ awayRoster.name }}: {{ adjustedScores.away }}</p>
            <p class="body-2">{{ homeRoster.name }}: {{ adjustedScores.home }}</p>

            <app-primary-button>Update</app-primary-button>
            <app-default-button class="ml-2" @click="editing = false">Cancel</app-default-button>
          </v-form>
        </v-col>
      </v-row>
    </v-sheet>
  </div>
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
import { adjustMatchupScores } from "../../../api/110yards/league"
import MatchupVs from "../../../components/league/matchup/MatchupVs.vue"
import scoreboard from "../../../mixins/scoreboard"
import MatchupHeader from "../../../components/league/matchup/MatchupHeader.vue"
import AppNumberField from "../../../components/inputs/AppNumberField.vue"
import AppPrimaryButton from "../../../components/buttons/AppPrimaryButton.vue"
import AppDefaultButton from "../../../components/buttons/AppDefaultButton.vue"
import eventBus from "../../../modules/eventBus"

export default {
  name: "matchup",
  components: {
    MatchupVs,
    MatchupHeader,
    AppNumberField,
    AppPrimaryButton,
    AppDefaultButton,
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
      editing: false,
      form: {
        away_adjustment: 0,
        home_adjustment: 0,
      },
    }
  },
  computed: {
    canEdit() {
      return !this.isCurrentWeek && (this.$root.isCommissioner || this.$store.state.isAdmin)
    },
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

    adjustedScores() {
      return {
        away: this.matchup.away_score + this.form.away_adjustment,
        home: this.matchup.home_score + this.form.home_adjustment,
      }
    },

    wasAdjusted() {
      return this.matchup && this.matchup.was_adjusted
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

    startEditing() {
      this.form.away_adjustment = this.matchup.away_adjustment || 0
      this.form.home_adjustment = this.matchup.home_adjustment || 0

      this.editing = true
    },

    async applyAdjustments() {
      let command = {
        league_id: this.leagueId,
        week_number: this.weekNumber,
        matchup_id: this.matchupId,
        away_adjustment: this.form.away_adjustment,
        home_adjustment: this.form.home_adjustment,
      }

      let valid = this.$refs.form.validate()
      if (!valid) {
        eventBus.$emit("show-error", "All fields are required")
        return
      }

      await adjustMatchupScores(this.leagueId, command)

      eventBus.$emit(
        "show-success",
        "Adjustments applied, it may take a moment for updated scores to appear throughout the site.",
      )

      this.editing = false
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
  },
}
</script>
