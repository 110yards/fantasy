<template>
  <div v-if="isAdmin">
    <v-row v-if="league" class="">
      <v-btn v-if="page == 'waivers'" :text="page != 'waivers'"> Waiver Results </v-btn>
    </v-row>

    <v-row class="mt-8">
      <waiver-results v-if="page == 'waivers'" :leagueId="leagueId" />
    </v-row>
  </div>
</template>

<script>
import { firestore } from "../../modules/firebase"
import WaiverResults from "./WaiverResults.vue"
export default {
  name: "LeagueAdmin",

  components: { WaiverResults },

  props: {
    leagueId: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      league: null,
      page: "waivers",
    }
  },

  computed: {
    isAdmin() {
      return this.$store.state.isAdmin
    },
  },

  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        let ref = firestore.doc(`league/${leagueId}`)
        this.$bind("league", ref)
      },
    },
  },
}
</script>
