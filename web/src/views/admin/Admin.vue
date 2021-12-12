<template>
  <v-card>
    <v-card-title>Admin Tools</v-card-title>

    <v-card-text>
      <v-btn class="caption" text @click="setView('status')">Status</v-btn>
      <v-btn class="caption" text @click="setView('problems')">Problems</v-btn>
      <v-btn class="caption" text @click="setView('leagues')">Leagues</v-btn>
      <v-btn class="caption" text @click="setView('maintenance')">Maintenance</v-btn>
      <v-btn class="caption" text @click="setView('sim')">Simulation</v-btn>
    </v-card-text>

    <v-card-text>
      <status v-if="view == 'status'" />
      <problems v-if="view == 'problems'" />
      <leagues v-if="view == 'leagues'" />
      <div v-if="view == 'maintenance'">
        TODO: Change year<br />
        TODO: End the year (stop jobs, change state)<br />
        TODO: Start the year (start jobs, change state, fetch list of games)<br />
      </div>
      <simulation v-if="view == 'sim'" />
    </v-card-text>
  </v-card>
</template>

<script>
import Problems from "../../components/admin/Problems.vue"
import Status from "../../components/admin/Status.vue"
import Leagues from "../../components/admin/Leagues.vue"
import Simulation from "../../components/admin/Simulation.vue"
export default {
  components: { Status, Problems, Leagues, Simulation },
  name: "Admin",
  data() {
    return {
      view: "status",
    }
  },

  methods: {
    setView(view) {
      this.view = view
    },
  },
}
</script>
