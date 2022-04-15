<template>
  <v-row v-if="archiveLeagues">
    <v-col cols="12" md="8">
      <v-card>
        <v-card-title>Play again in {{ currentSeason }}:</v-card-title>
        <v-card-text>
          <div v-for="league in archiveLeagues" :key="league.leagueId">
            <v-row>
              <v-col cols="12" class="title">
                <router-link
                  :to="{
                    name: 'league',
                    params: { leagueId: league.id },
                  }"
                  >{{ league.league_name }}</router-link
                >
              </v-col>
            </v-row>
          </div>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
export default {
  name: "ArchiveLeagues",

  props: {
    archiveLeagues: {
      type: Array,
      required: true,
    },
  },

  computed: {
    currentSeason() {
      return this.$root.currentSeason
    },
  },
}
</script>
