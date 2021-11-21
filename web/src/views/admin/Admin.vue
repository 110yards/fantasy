<template>
  <v-card>
    <v-card-title>Admin Tools</v-card-title>

    <v-card-text>
      <v-btn class="caption" text @click="setView('status')">Status</v-btn>
      <v-btn class="caption" text @click="setView('problems')">Problems</v-btn>
      <v-btn class="caption" text @click="setView('leagues')">Leagues</v-btn>
    </v-card-text>

    <v-card-text>
      <status v-if="view == 'status'" />
      <problems v-if="view == 'problems'" />
      <leagues v-if="view == 'leagues'" />
    </v-card-text>
  </v-card>
</template>

<script>
import Problems from "../../components/admin/Problems.vue"
import Status from "../../components/admin/Status.vue"
import Leagues from "../../components/admin/Leagues.vue"
export default {
  components: { Status, Problems, Leagues },
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
