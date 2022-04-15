<template>
  <v-card v-if="seasonSummary">
    <v-card-title class="heading-6">{{ title }}</v-card-title>

    <v-card-text>
      <p class="font-weight-medium">
        <span>Champion: </span>
        <v-icon small color="grey" class="mr-1">mdi-trophy</v-icon>

        <span>{{ this.seasonSummary.champion.name }}</span>
      </p>
      <p class="font-weight">
        <span>Runner-up: </span>
        <span>{{ this.seasonSummary.runner_up.name }}</span>
      </p>
    </v-card-text>

    <v-card-title class="subtitle-1">Regular Season Standings</v-card-title>
    <v-card-text>
      <v-row v-for="roster in rosters" :key="roster.id" class="mt-0">
        <v-col cols="10" md="6" class="roster-name">
          {{ roster.regular_season_rank }}.
          <span>{{ roster.name }}</span>
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
    season: {
      type: Number,
      required: false,
    },
  },
  data() {
    return {
      seasonSummary: null,
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

      let path = `league/${this.leagueId}/seasons/${season}`
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
  },
}
</script>
