<template>
  <v-card>
    <v-card-title>Last Pick</v-card-title>
    <v-card-text v-if="previousSlot">
      {{ previousSlot.result }}
    </v-card-text>
    <v-card-text v-else>
      N/A
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: "last-draft-pick-card",
  props: {
    draft: {
      type: Object,
      required: true,
    },
  },
  computed: {
    previousSlot() {
      if (!this.draft) return null

      let completedPicks = this.draft.slots.filter(s => s.completed == true)

      if (completedPicks.length > 0) {
        return completedPicks[completedPicks.length - 1]
      }

      return null
    },
  },
}
</script>
