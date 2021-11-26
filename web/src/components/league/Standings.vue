<template>
  <section id="standings">
    <v-card>
      <v-card-title class="subtitle-1">Standings</v-card-title>

      <v-card-text>
        <v-row>
          <v-col cols="6" md="6" class="caption"></v-col>
          <v-col cols="2" md="1" class="caption">Pts</v-col>
          <v-col cols="2" md="1" class="caption text-center">LW</v-col>
          <v-col cols="2" class="caption text-center">$</v-col>
        </v-row>

        <v-row v-for="roster in rosters" :key="roster.id" class="mt-0">
          <v-col cols="6" md="6" class="roster-name">
            <router-link
              :to="{
                name: 'roster',
                params: { leagueId: leagueId, rosterId: roster.id },
              }"
            >
              <span>{{ roster.name }}</span>

              <v-icon v-if="isCommissionersRoster(roster)" class="ml-2 commissioner">mdi-star</v-icon>
              <span v-if="isCommissionersRoster(roster)" class="d-sr-only">Commissioner</span>
            </router-link>
            <div class="caption">
              {{ roster.record }}
              <!-- <span> - ${{ roster.waiver_budget }}</span> -->
            </div>
          </v-col>
          <v-col cols="2" md="1" class="px-0">{{ formatScore(roster.points_for) }}</v-col>
          <v-col cols="2" md="1" class="px-0 text-center">{{ roster.last_week_result }}</v-col>
          <v-col cols="2" class="px-0 text-center">${{ roster.waiver_budget }}</v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </section>
</template>

<style scoped>
.v-icon.commissioner {
  color: yellow;
  font-size: 0.9em;
}
</style>

<script>
import { firestore } from "../../modules/firebase"
import { formatScore } from "../../modules/formatter"

export default {
  name: "league-index",
  props: {
    league: {
      type: Object,
      required: true,
    },
  },
  components: {},
  data() {
    return {
      rosters: [],
    }
  },
  computed: {
    leagueId() {
      return this.league.id
    },
    isCommissioner() {
      if (this.league == null || this.$store.state.currentUser == null) return false

      return this.league.commissioner_id == this.$store.state.currentUser.uid
    },

    scheduleGenerated() {
      return this.league && this.league.schedule_generated
    },
  },
  methods: {
    isCommissionersRoster(roster) {
      if (this.league == null || this.$store.state.currentUser == null) return false

      return this.league.commissioner_id == roster.id
    },

    formatScore(score) {
      return formatScore(score)
    },
  },

  watch: {
    league: {
      immediate: true,
      handler(league) {
        this.$bind("rosters", firestore.collection("league").doc(league.id).collection("roster").orderBy("rank"))
      },
    },
  },
}
</script>
