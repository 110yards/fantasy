<template>
  <v-card class="draft-events">
    <v-card-title>Draft Events</v-card-title>
    <v-card-text>
      <p v-for="(event, index) in events" :key="index">
        {{ event }}
      </p>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.draft-events {
  display: flex !important;
  flex-direction: column;
  height: 200px;
}

.draft-events >>> .v-card__text {
  flex-grow: 1;
  overflow: auto;
}
</style>

<script>
export default {
  props: {
    events: {
      type: Array,
      default: [],
    },
  },
}
</script>
