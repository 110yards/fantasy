<template>
  <v-card class="draft-picks">
    <v-card-title>{{ title }}</v-card-title>
    <v-card-text>
      <p v-for="slot in slots" :key="slot.pick_number">
        Pick {{ slot.pick_number }} -
        <span v-if="!slot.completed">{{ getRosterName(slot.roster_id) }}</span>
        <span v-if="slot.completed">{{ slot.result }}</span>
      </p>

      <p v-if="slots.length == 0">N/A</p>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.draft-picks {
  display: flex !important;
  flex-direction: column;
  height: 160px;
}

.draft-picks >>> .v-card__text {
  flex-grow: 1;
  overflow: auto;
}
</style>

<script>
export default {
  name: "draft-picks-list",
  props: {
    title: {
      type: String,
      required: true,
    },
    slots: {
      type: Array,
      required: true,
    },
    rosters: {
      type: Array,
      required: true,
    },
  },

  computed: {},

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
