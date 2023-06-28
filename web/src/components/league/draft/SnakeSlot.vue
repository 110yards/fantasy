<template>
  <v-card class="snake-draft-picks" v-if="draft">
    <v-card-title>Draft</v-card-title>
    <v-card-text>
      <p v-for="slot in draft.slots" :key="slot.pick_number">
        Pick {{ slot.pick_number }} - {{ getRosterName(slot.roster_id) }}
        <span v-if="slot.completed"> - {{ slot.player.player_id }} </span>
      </p>
    </v-card-text>
    <v-card-text v-if="yourTurn"> Your turn! </v-card-text>
  </v-card>
</template>

<style scoped>
.snake-draft-picks {
  display: flex !important;
  flex-direction: column;
  height: 200px;
}

.snake-draft-picks >>> .v-card__text {
  flex-grow: 1;
  overflow: auto;
}
</style>

<script>
export default {
  name: "snake-slot",
  props: {
    draft: {
      type: Object,
      required: true,
    },
    rosters: {
      type: Array,
      required: true,
    },
  },

  computed: {
    currentPickNumber() {
      let currentSlot = this.draft.slots.find(s => s.completed == false)
      return currentSlot.pick_number
    },
    previousSlot() {
      if (!this.draft) return null
    },

    yourTurn() {
      return this.currentSlot.roster_id == this.currentRosterId
    },

    currentSlot() {
      if (!this.draft || !this.rosters) return null

      let nextPick = this.draft.slots.find(s => s.completed == false)

      return nextPick
    },
  },

  methods: {
    getRoster(rosterId) {
      return this.rosters.find(r => r.id == rosterId)
    },

    getRosterName(rosterId) {
      let roster = this.getRoster(rosterId)

      return roster != null ? roster.name : ""
    },
  },
}
</script>
