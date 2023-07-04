<template>
  <v-card>
    <v-card-title>Admin Tools</v-card-title>

    <v-card-text>
      <v-btn class="caption" text @click="setView('players')"
        >Players <v-badge v-if="highlightPlayers" class="ml-2" dot color="green"
      /></v-btn>
    </v-card-text>

    <v-card-text>
      <players v-if="view == 'players'" />
    </v-card-text>
  </v-card>
</template>

<script>
import Players from "../../components/mod/Players.vue"

export default {
  components: { Players },
  name: "Mod",
  data() {
    return {
      view: "players",
    }
  },

  computed: {
    highlightPlayers() {
      return this.$root.anyPlayerApprovals
    },
  },

  methods: {
    setView(view) {
      this.view = view
    },
  },
}
</script>
