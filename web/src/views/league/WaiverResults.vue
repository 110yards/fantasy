<template>
  <div>
    <v-col cols="12" md="6">
      <app-select v-model="weekNumber" label="Week number" :items="availableWeeks" required />
    </v-col>

    <v-col cols="12">
      <v-simple-table v-if="week">
        <template>
          <thead>
            <tr>
              <th>Roster</th>
              <th>Player</th>
              <th>Bid</th>
              <th>Drop Player</th>
              <th>Result</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(bid, index) in week.waiver_bids" :key="index">
              <td>
                {{ getRosterName(bid) }}
              </td>
              <td><player-link :leagueId="leagueId" :player="bid.player" :showTeamLogo="false" /></td>
              <td>${{ bid.amount }}</td>
              <td>
                <player-link
                  v-if="bid.drop_player"
                  :leagueId="leagueId"
                  :player="bid.drop_player"
                  :showTeamLogo="false"
                />
                <span v-else>N/A</span>
              </td>
              <td>
                {{ getBidResult(bid.result) }}
              </td>
            </tr>
          </tbody>
        </template>
      </v-simple-table>
    </v-col>
  </div>
</template>

<script>
import { waiverBidResult } from "../../api/110yards/constants"
import AppSelect from "../../components/inputs/AppSelect.vue"
import PlayerLink from "../../components/player/PlayerLink.vue"
import { firestore } from "../../modules/firebase"
export default {
  components: { AppSelect, PlayerLink },
  name: "WaiverResults",
  props: {
    leagueId: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      weekNumber: (this.$root.state.current_week - 1).toString(),
      week: null,
      rosters: null,
    }
  },

  computed: {
    currentWeek() {
      return this.$root.state.current_week
    },
    isAdmin() {
      return this.$store.state.isAdmin
    },
    availableWeeks() {
      let weeks = []

      for (let i = 1; i < this.currentWeek; i++) {
        weeks.push({ text: `${i}`, value: `${i}` })
      }

      return weeks
    },
  },

  methods: {
    getBidResult(result) {
      return waiverBidResult.getText(result)
    },

    getRosterName(bid) {
      let roster = this.rosters.filter(r => r.id == bid.roster_id)
      return roster.length > 0 ? roster[0].name : null
    },

    configureWeekBinding() {
      let ref = firestore.doc(`league/${this.leagueId}/week/${this.weekNumber}`)
      this.$bind("week", ref)
    },

    configureRostersBinding() {
      let ref = firestore.collection(`league/${this.leagueId}/roster`)
      this.$bind("rosters", ref)
    },
  },

  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        if (leagueId) {
          this.configureWeekBinding()
          this.configureRostersBinding()
        }
      },
    },

    weekNumber: {
      handler(_) {
        this.configureWeekBinding()
      },
    },
  },
}
</script>
