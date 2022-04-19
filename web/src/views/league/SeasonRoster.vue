<template>
  <v-card v-if="roster">
    <v-card-title>
      {{ roster.name }}
      <v-icon v-if="wasChampion" small color="grey" class="mr-1">mdi-trophy</v-icon>
    </v-card-title>
    <v-card-subtitle>{{ roster.record }} ({{ formattedRank }})</v-card-subtitle>
    <v-card-text>
      <v-container>
        <v-row v-for="position in sortedSpots" :key="position.position_id">
          <v-col cols="2" md="1"> {{ position.name }}</v-col>

          <v-col>
            <router-link :to="{ name: 'league-player', params: { leagueId: leagueId, playerId: position.player_id } }">
              {{ position.player_name }}
            </router-link>
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script>
import Lineup from "../../components/league/roster/Lineup.vue"
import PlayerLink from "../../components/player/PlayerLink.vue"
import { firestore } from "../../modules/firebase"

export default {
  name: "SeasonRoster",
  components: { Lineup, PlayerLink },

  props: {
    leagueId: {
      type: String,
      required: true,
    },
    rosterId: {
      type: String,
      required: true,
    },
    seasonId: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      season: null,
    }
  },

  computed: {
    roster() {
      if (!this.season) return null
      let matches = this.season.rosters.filter(x => x.roster_id == this.rosterId)

      return matches.length == 1 ? matches[0] : null
    },

    formattedRank() {
      if (!this.roster) return null

      switch (this.roster.regular_season_rank) {
        case 1:
          return "1st"
        case 2:
          return "2nd"
        case 3:
          return "3rd"
        default:
          return `${this.roster.regular_season_rank}th`
      }
    },

    wasChampion() {
      if (!this.roster) return false

      return this.roster.roster_id == this.season.champion.roster_id
    },

    sortedSpots() {
      if (!this.roster) return null

      return this.roster.positions.sort((a, b) => (a.position_id > b.position_id ? 1 : -1))
    },
  },

  methods: {
    configureReferences() {
      if (!this.leagueId || !this.seasonId || !this.rosterId) return
      let path = `league/${this.leagueId}/seasons/${this.seasonId}`
      let ref = firestore.doc(path)
      this.$bind("season", ref)
    },
  },

  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        this.configureReferences()
      },
    },
    rosterId: {
      immediate: true,
      handler(rosterId) {
        this.configureReferences()
      },
    },
    seasonId: {
      immediate: true,
      handler(seasonId) {
        this.configureReferences()
      },
    },
  },
}
</script>
