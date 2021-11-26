<template>
  <v-card v-if="seasonSummary">
    <v-card-title class="heading-6">{{ this.currentSeason }}</v-card-title>

    <v-card-text>
      <p class="font-weight-medium">
        <span>Champion: </span>
        <v-icon small color="grey" class="mr-1">mdi-trophy</v-icon>
        <router-link
          :to="{
            name: 'roster',
            params: { leagueId: leagueId, rosterId: this.seasonSummary.champion.roster_id },
          }"
        >
          <span>{{ this.seasonSummary.champion.name }}</span>
        </router-link>
      </p>
      <p class="font-weight">
        <span>Runner-up: </span>
        <router-link
          :to="{
            name: 'roster',
            params: { leagueId: leagueId, rosterId: this.seasonSummary.runner_up.roster_id },
          }"
        >
          <span>{{ this.seasonSummary.runner_up.name }}</span>
        </router-link>
      </p>
    </v-card-text>

    <v-card-title class="subtitle-1">Regular Season Standings</v-card-title>
    <v-card-text>
      <v-row v-for="roster in seasonSummary.rosters" :key="roster.id" class="mt-0">
        <v-col cols="10" md="6" class="roster-name">
          {{ roster.regular_season_rank }}.
          <router-link
            :to="{
              name: 'roster',
              params: { leagueId: leagueId, rosterId: roster.roster_id },
            }"
          >
            <span>{{ roster.name }}</span>
          </router-link>
        </v-col>
        <v-col cols="2" md="1" class="px-0">{{ roster.record }}</v-col>
      </v-row>
    </v-card-text>
  </v-card>

  <v-card v-else> The season has ended, hope to see you back next year!</v-card>
</template>

<script>
import { firestore } from "../../modules/firebase"

export default {
  props: {
    leagueId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      seasonSummary: null,
    }
  },

  computed: {
    currentSeason() {
      return this.$root.state?.current_season
    },
  },

  methods: {
    bindReferences() {
      if (!this.leagueId || !this.currentSeason) return

      let path = `league/${this.leagueId}/seasons/${this.currentSeason}`
      this.$bind("seasonSummary", firestore.doc(path))
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
    currentSeason: {
      immediate: true,
      handler(currentSeason) {
        if (currentSeason == null) return
        this.bindReferences()
      },
    },
  },
}
</script>
