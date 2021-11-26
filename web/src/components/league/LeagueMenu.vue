<template>
  <v-row v-if="league" class="">
    <v-btn text :to="{ name: 'league-settings', params: { leagueId: league.id } }">League settings</v-btn>
    <v-btn text :to="{ name: 'league-schedule', params: { leagueId: league.id } }">Schedule</v-btn>

    <v-btn v-if="isCommissioner || isAdmin" text :to="{ name: 'commissioner', params: { leagueId: league.id } }">
      Commissioner
    </v-btn>

    <v-btn v-if="isAdmin" text :to="{ name: 'league-admin', params: { leagueId: league.id } }"> Admin </v-btn>
  </v-row>
</template>

<script>
export default {
  name: "LeagueMenu",

  props: {
    league: {
      type: Object,
      required: true,
    },
  },

  computed: {
    isCommissioner() {
      if (this.league == null || this.$store.state.currentUser == null) return false

      return this.league.commissioner_id == this.$store.state.currentUser.uid
    },

    isAdmin() {
      return this.$store.state.isAdmin
    },
  },
}
</script>
