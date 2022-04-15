<template>
  <div v-if="isAdmin">
    <waiver-results v-if="page == 'waivers'" :leagueId="leagueId" />
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
