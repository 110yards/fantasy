<template>
  <v-card>
    <v-card-title>Moderator Tools</v-card-title>

    <v-card-text>
      <v-btn class="caption" text @click="setView('transactions')">Transactions</v-btn>
      <v-btn class="caption" text @click="setView('corrections')">Corrections</v-btn>
      <v-btn v-if="enablePlayerApprovals" class="caption" text @click="setView('players')">Players <v-badge
          v-if="highlightPlayers" class="ml-2" dot color="green" /></v-btn>
    </v-card-text>

    <v-card-text>
      <Transactions v-if="view == 'transactions'" />
      <Corrections v-if="view == 'corrections'" />
      <players v-if="view == 'players'" />
    </v-card-text>
  </v-card>
</template>

<script>
import Corrections from "../../components/mod/corrections/Corrections.vue"
import Players from "../../components/mod/Players.vue"
import Transactions from "../../components/mod/Transactions.vue"

export default {
  components: { Players, Transactions, Corrections },
  name: "Mod",
  data() {
    return {
      view: "corrections",
    }
  },
  computed: {
    highlightPlayers() {
      return this.$root.anyPlayerApprovals
    },
    enablePlayerApprovals() {
      return this.$root.enablePlayerApprovals
    },
  },
  methods: {
    setView(view) {
      this.view = view
    },
  },
}
</script>
