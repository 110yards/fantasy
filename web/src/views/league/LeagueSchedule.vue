<template>
  <div v-if="league && schedule">
    <league-menu :league="league" />

    <v-card class="mt-4">
      <v-card-title>Playoff settings</v-card-title>
      <v-card-text>
        <p>
          <app-form-label>
            Playoff teams: {{ playoffType }}
            <span v-if="schedule.enable_loser_playoff">+ bottom 2 (loser playoff)</span>
          </app-form-label>
        </p>

        <p>
          <app-form-label>First playoff week: {{ schedule.first_playoff_week }}</app-form-label>
        </p>
      </v-card-text>
    </v-card>

    <v-card class="mt-4">
      <v-card-title>Schedule</v-card-title>
      <v-card-text>
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
      </v-card-text>
    </v-card>
    <v-card class="mt-5">
      <v-card-text></v-card-text>
    </v-card>
  </div>
  <div v-else>League schedule has not been set up by the commissioner yet.</div>
</template>

<script>
import AppFormLabel from "../../components/inputs/AppFormLabel.vue"
import LeagueMenu from "../../components/league/LeagueMenu.vue"
import { firestore } from "../../modules/firebase"

export default {
  name: "LeagueSchedule",

  components: { LeagueMenu, AppFormLabel },
  props: {
    leagueId: { type: String, required: true },
  },

  data() {
    return {
      league: null,
      schedule: null,
      rosters: [],
      playoffTypes: [],
    }
  },

  computed: {
    matchupsPerWeek() {
      return this.rosters.length / 2
    },

    playoffType() {
      if (!this.schedule) return

      let type = this.playoffTypes.filter(x => x.id == this.schedule.playoff_type)
      return type.length == 1 ? type[0].name : this.schedule.playoff_type
    },
  },

  methods: {
    configureBindings() {
      let leagueRef = firestore.doc(`league/${this.leagueId}`)
      let configRef = leagueRef.collection("config")
      let scheduleConfigRef = configRef.doc("schedule")
      let rostersRef = leagueRef.collection("roster")
      let playoffTypesRef = firestore.collection("playoff-types")

      this.$bind("league", leagueRef)
      this.$bind("schedule", scheduleConfigRef)
      this.$bind("rosters", rostersRef)
      this.$bind("playoffTypes", playoffTypesRef)
    },
  },

  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        if (leagueId) {
          this.configureBindings()
        }
      },
    },
  },
}
</script>
