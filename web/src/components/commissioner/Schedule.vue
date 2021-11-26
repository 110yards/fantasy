<template>
  <div>
    <v-row v-if="!enoughTeams">
      <v-alert type="warning"> League must have an even number of teams. </v-alert>
    </v-row>

    <v-row v-else>
      <v-col cols="12" v-if="!league.registration_closed">
        <v-alert type="warning">Generating the schedule will lock registration</v-alert>
      </v-col>
      <v-col cols="12" md="6">
        <v-form ref="form" @submit.prevent="submit()">
          <app-select
            v-if="!leagueStarted"
            v-model="form.playoffType"
            :items="eligiblePlayoffTypes"
            label="Playoff type"
            :rules="playoffTypeRules"
            required
          />
          <p v-else>
            <app-form-label>Playoff teams: {{ form.playoffType }}</app-form-label>
          </p>

          <app-select
            v-if="!leagueStarted"
            v-model="form.firstPlayoffWeek"
            label="First playoff week"
            :items="weekCounts"
            :rules="firstPlayoffWeekRules"
            required
          />
          <p v-else>
            <app-form-label>First playoff week: {{ form.firstPlayoffWeek }}</app-form-label>
          </p>

          <div v-if="canUseLoserPlayoff()">
            <app-form-label
              >Enable loser playoff? <small>(A playoff matchup between the last place teams)</small></app-form-label
            >

            <v-layout align-center class="mb-8"
              ><v-simple-checkbox v-model="form.enableLoserPlayoff" class="form-check-input" :ripple="false" />
              <span>Yes</span>
            </v-layout>
          </div>
          <app-primary-button v-if="!leagueStarted" type="submit" class="btn btn-default">
            Generate schedule
          </app-primary-button>
          <saved-indicator :saved="saved" />
        </v-form>
      </v-col>
    </v-row>

    <v-row v-if="hasSchedule">
      <v-simple-table>
        <template v-slot:default>
          <thead>
            <tr>
              <th>Week</th>
              <th v-for="x in matchupsPerWeek" :key="x">Matchup {{ x }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="week in schedule.weeks" :key="week.week_number">
              <th>{{ week.week_number }}</th>
              <td v-for="(matchup, index) in week.matchups" :key="index">
                <span v-if="matchup.type == 'regular'">{{ matchup.away.name }} @ {{ matchup.home.name }}</span>
                <span v-else>{{ matchup.type_display }}</span>
              </td>
            </tr>
          </tbody>
        </template>
      </v-simple-table>
    </v-row>

    <v-row>
      <start-draft :league="league" />
    </v-row>
  </div>
</template>

<style scoped>
option.ideal {
  font-weight: bold;
}

.table {
  margin-top: 2em;
}

.table th,
.table td {
  padding: 0.5em;
}

.table tr:nth-child(even) {
  background-color: var(--bg-color-secondary);
}
</style>

<script>
import _ from "lodash"
import { firestore } from "../../modules/firebase"
import * as leagueService from "../../api/110yards/league"
import SavedIndicator from "../SavedIndicator"
import StartDraft from "./StartDraft"
import AppSelect from "../inputs/AppSelect.vue"
import AppFormLabel from "../inputs/AppFormLabel.vue"
import AppPrimaryButton from "../buttons/AppPrimaryButton.vue"

// TODO: move some of the logic in these methods into a service object

export default {
  name: "schedule",
  components: {
    SavedIndicator,
    StartDraft,
    AppSelect,
    AppFormLabel,
    AppPrimaryButton,
  },
  props: {
    leagueId: String,
    leagueStarted: Boolean,
  },
  data() {
    return {
      league: {},
      schedule: [],
      rosters: [],
      playoffTypes: [],
      form: {
        playoffType: null,
        firstPlayoffWeek: null,
        enableLoserPlayoff: false,
      },
      playoffTypeRules: [v => !!v || "Playoff type is required"],
      firstPlayoffWeekRules: [v => !!v || "First playoff week is required"],
      saved: false,
    }
  },
  computed: {
    hasSchedule() {
      return (
        this.league &&
        this.league.schedule_generated &&
        this.schedule &&
        this.schedule.weeks &&
        this.schedule.weeks.length > 0
      )
    },

    enoughTeams() {
      return this.rosters.length % 2 == 0
    },

    eligiblePlayoffTypes() {
      let types = this.playoffTypes.filter(x => x.id <= this.rosters.length)

      let selections = []
      for (let type of types) {
        selections.push({ text: type.name, value: `${type.id}` })
      }
      return selections
    },

    weekCounts() {
      const lastWeek = process.env.VUE_APP_SEASON_WEEKS

      let counts = []
      for (let i = 1; i <= lastWeek; i++) {
        counts.push({ text: `${i}`, value: `${i}` })
      }
      return counts
    },

    matchupsPerWeek() {
      return this.rosters.length / 2
    },
  },
  methods: {
    isIdeal(x) {
      return (x - 1) % (this.rosters.length - 1) == 0
    },

    canUseLoserPlayoff() {
      let canUse = this.form.playoffType && this.rosters.length - this.form.playoffType >= 2

      if (!canUse && this.form.enableLoserPlayoff) this.form.enableLoserPlayoff = false

      return canUse
    },

    async submit() {
      console.log("submit")
      let valid = await this.$refs.form.validate()

      console.log(valid)

      if (!valid) return

      this.save()
    },

    async save() {
      let user = this.$store.state.currentUser
      let options = {
        playoff_type: parseInt(this.form.playoffType),
        first_playoff_week: parseInt(this.form.firstPlayoffWeek),
        enable_loser_playoff: this.form.enableLoserPlayoff || false,
      }

      await leagueService.generateSchedule(user, this.leagueId, options)
      this.saved = true
    },

    bindSchedule(leagueId) {
      this.$bind("schedule", firestore.collection("league").doc(leagueId).collection("config").doc("schedule"))
    },

    bindLeague(leagueId) {
      this.$bind("league", firestore.doc(`league/${leagueId}`))
    },

    bindManagers(leagueId) {
      this.$bind("rosters", firestore.collection(`league/${leagueId}/roster`))
    },

    bindPlayoffTypes() {
      this.$bind("playoffTypes", firestore.collection(`playoff-types`))
    },
  },
  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        if (leagueId == null) return
        this.bindLeague(leagueId)
        this.bindSchedule(leagueId)
        this.bindManagers(leagueId)
      },
    },

    schedule: {
      immediate: true,
      handler(schedule) {
        if (schedule == null || schedule.length == 0) return
        this.form.playoffType = `${schedule.playoff_type}`
        this.form.firstPlayoffWeek = `${schedule.first_playoff_week}`
        this.form.enableLoserPlayoff = schedule.enable_loser_playoff
      },
    },
  },

  mounted: function () {
    this.bindPlayoffTypes()
  },
}
</script>
