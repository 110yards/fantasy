<template>
  <div>
    <league-header v-if="league" :leagueName="league.name" :leagueId="league.id" :season="season" />

    <v-card v-if="seasonSummary">
      <v-card-title class="heading-6">{{ title }}</v-card-title>

      <v-card-text>
        <p class="font-weight-medium">
          <span>Champion: </span>
          <v-icon small color="grey" class="mr-1">mdi-trophy</v-icon>
          <span>
            <router-link
              :to="{
                name: 'leagueSeasonRoster',
                params: { season: seasonSummary.id, leagueId: leagueId, rosterId: seasonSummary.champion.roster_id },
              }"
            >
              {{ this.seasonSummary.champion.name }}
            </router-link>
          </span>
        </p>
        <p class="font-weight">
          <span>Runner-up: </span>
          <router-link
            :to="{
              name: 'leagueSeasonRoster',
              params: { season: seasonSummary.id, leagueId: leagueId, rosterId: seasonSummary.runner_up.roster_id },
            }"
          >
            {{ this.seasonSummary.runner_up.name }}
          </router-link>
        </p>
      </v-card-text>

      <v-card-title class="subtitle-1">Regular Season Standings</v-card-title>
      <v-card-text>
        <v-row v-for="roster in rosters" :key="roster.id" class="mt-0">
          <v-col cols="10" md="6" class="roster-name">
            {{ roster.regular_season_rank }}.
            <router-link
              :to="{
                name: 'leagueSeasonRoster',
                params: { season: seasonSummary.id, leagueId: leagueId, rosterId: roster.roster_id },
              }"
            >
              {{ roster.name }}
            </router-link>
          </v-col>
          <v-col cols="2" md="1" class="px-0">{{ roster.record }}</v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { firestore } from "../../modules/firebase"
import LeagueHeader from "./LeagueHeader.vue"

export default {
  components: { LeagueHeader },
  props: {
    leagueId: {
      type: String,
      required: true,
    },
    season: {
      required: false,
    },
  },
  data() {
    return {
      seasonSummary: null,
      league: null,
    }
  },

  computed: {
    title() {
      return this.seasonSummary ? this.seasonSummary.id : ""
    },

    rosters() {
      return this.seasonSummary
        ? this.seasonSummary.rosters.sort((a, b) => a.regular_season_rank - b.regular_season_rank)
        : null
    },
  },

  methods: {
    bindReferences() {
      if (!this.leagueId) return

      let season = this.season || 2021 // Future seasons will always be assigned to the league object and passed in here.

      let seasonPath = `league/${this.leagueId}/seasons/${season}`
      this.$bind("seasonSummary", firestore.doc(seasonPath))

      let leaguePath = `league/${this.leagueId}`
      this.$bind("league", firestore.doc(leaguePath))
    },
  },

  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        if (leagueId == null) return
        this.bindReferences()
      },
    },
  },
}
</script>
