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

          <div v-if="canUseLoserPlayoff()">
            <app-form-label
              >Enable loser playoff? <small>(A playoff matchup between the last place teams)</small></app-form-label
            >

            <v-layout align-center class="mb-8"
              ><v-simple-checkbox v-model="form.enableLoserPlayoff" class="form-check-input" :ripple="false" />
              <span>Yes</span>
            </v-layout>
          </div>

          <p class="caption" v-if="!leagueStarted">
            Teams on bye are listed beside each week.<br /><br />
            Selecting a week marked "balanced" will ensure all teams play each other an equal number of times.
            <br /><br />
            For a better experience, avoid running your league too long. The longer your regular season, the more likely
            your playoffs will be impacted by teams resting starters.
          </p>

          <p class="caption" v-if="!leagueStarted"></p>
          <p v-else>
            <app-form-label>First playoff week: {{ form.firstPlayoffWeek }}</app-form-label>
          </p>

          <app-primary-button v-if="!leagueStarted" type="submit" class="btn btn-default">
            Generate schedule
          </app-primary-button>
          <start-draft :league="league" />
          <saved-indicator :saved="saved" />
        </v-form>
      </v-col>
    </v-row>

    <v-row v-if="hasSchedule">
      <v-card v-for="week in schedule.weeks" :key="week.week_number" class="col-md-4 col-12 text-center">
        <v-card-title class="justify-center"> Week {{ week.week_number }} </v-card-title>
        <v-card-subtitle> Byes: {{ getByeTeams(week.week_number) }} </v-card-subtitle>
        <v-card-text>
          <div v-for="(matchup, index) in week.matchups" :key="index">
            <div v-if="matchup.type == 'regular'">
              <span class="d-block overline matchup-heading">Matchup {{ matchup.id }}</span>
              <span class="d-block body-2">{{ matchup.away.name }}</span>
              <span class="d-block caption">vs</span>
              <span class="d-block body-2">{{ matchup.home.name }}</span>
            </div>
            <div v-else>
              <span class="matchup-heading overline">{{ matchup.type_display }}</span>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-row>

    <v-row>
      <start-draft :league="league" />
    </v-row>
  </div>
</template>

<style scoped>
.table {
  margin-top: 2em;
}

.table th,
.table td {
  padding: 0.5em;
}

.matchup-heading {
  color: var(--color-secondary);
}

.v-card:nth-child(even) {
  background-color: var(--bg-color-secondary);
}
</style>

<script>
import _ from "lodash"
import { firestore, rtdb } from "../../modules/firebase"
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
      weekCounts: [],
      seasonSchedule: null,
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

    matchupsPerWeek() {
      return this.rosters.length / 2
    },
  },
  methods: {
    getWeekKey(weekNumber) {
      return `W${weekNumber.toString().padStart(2, "0")}`
    },

    getByeTeams(weekNumber) {
      if (!this.seasonSchedule) return ""

      let key = this.getWeekKey(weekNumber)
      let teams = this.seasonSchedule.weeks[key].bye_teams
      return teams.join(", ").toUpperCase()
    },

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

    async setupWeekCounts(rosterCount) {
      let path = `/schedules/${this.$root.state.current_season}`
      let schedule = (await rtdb.ref(path).get()).val()
      this.seasonSchedule = schedule

      const firstWeek = this.$root.state.current_week + 1
      const lastWeek = schedule.week_count

      let counts = []
      let opponentCount = rosterCount - 1

      for (let i = firstWeek; i <= lastWeek; i++) {
        let ideal = rosterCount > 2 && (i - 1) % opponentCount == 0
        // zero padded 2 digit
        let weekKey = this.getWeekKey(i)

        let byes = schedule.weeks[weekKey].bye_teams
        let byesString = byes.length > 0 ? byes.join(", ") : ""
        byesString = byesString.toUpperCase()

        let marker = ""
        if (ideal) {
          marker = ` - ${byesString} (balanced)`
        } else {
          marker = ` - ${byesString}`
        }

        counts.push({ text: `${i}${marker}`, value: `${i}` })
      }

      this.weekCounts = counts
    },
  },
  watch: {
    rosters: {
      handler(rosters) {
        if (rosters == null || rosters.length == 0) return

        this.setupWeekCounts(rosters.length)
      },
    },

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
        this.form.firstPlayoffWeek = schedule.first_playoff_week ? `${schedule.first_playoff_week}` : ""
        this.form.enableLoserPlayoff = schedule.enable_loser_playoff
      },
    },
  },

  mounted: function () {
    this.bindPlayoffTypes()
  },
}
</script>
