<template>
  <v-row dense>
    <v-col cols="12" md="10">
      <h2 class="brand">{{ leagueName }}</h2>
    </v-col>

    <v-col cols="12" md="2"><season-list :leagueId="leagueId" :season="season" /></v-col>
  </v-row>
</template>

<script>
import SeasonList from "./SeasonList.vue"

export default {
  components: { SeasonList },

  props: {
    leagueId: {
      type: String,
      required: true,
    },
    leagueName: {
      type: String,
      required: true,
    },
    season: {
      type: String,
      required: false,
    },
  },
}
</script>
