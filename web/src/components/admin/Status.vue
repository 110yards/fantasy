<template>
  <v-row>
    <v-col md="6" cols="12">
      <v-chip class="ma-2" :color="apiStatusColor">
        <v-icon left>mdi-wrench</v-icon>
        <span>API status {{ apiStatus.status }}</span>
      </v-chip>
      <v-chip class="ma-2" color="blue" outlined>
        <v-icon left>mdi-account</v-icon>
        <span>Users: {{ stats.verified_user_count }}</span>
      </v-chip>
      <v-chip class="ma-2" color="green" outlined>
        <v-icon left>mdi-fire</v-icon>
        <span>Active Leagues {{ stats.active_league_count }}</span>
      </v-chip>
      <v-chip class="ma-2" color="red" outlined>
        <v-icon left>mdi-fire</v-icon>
        <span>Total Leagues {{ stats.league_count }}</span>
      </v-chip>
    </v-col>
  </v-row>
</template>

<script>
import { status } from "../../api/110yards/root"
import AppFormLabel from "../inputs/AppFormLabel.vue"
import { firestore } from "../../modules/firebase"

export default {
  components: { AppFormLabel },
  name: "status",

  data() {
    return {
      smokeTestResults: null,
      apiStatus: {},
      stats: {
        league_count: 0,
        verified_user_count: 0,
      },
    }
  },

  computed: {
    apiStatusColor() {
      return this.apiStatus.status == "ok" ? "green" : "red"
    },
    currentUser() {
      return this.$store.state.currentUser
    },
  },

  methods: {
    async getStatus() {
      this.apiStatus = await status()
    },

    configureReferences() {
      let statsRef = firestore.doc("/admin/stats")

      this.$bind("stats", statsRef)
    },
  },

  watch: {
    currentUser: {
      immediate: true,
      handler(user) {
        if (user) {
          this.configureReferences()
        }
      },
    },
  },

  created() {
    this.getStatus()
  },
}
</script>
