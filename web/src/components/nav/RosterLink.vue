<template>
  <v-btn
    text
    class="nav-item nav-link"
    :to="{
      name: 'roster',
      params: { leagueId: leagueId, rosterId: userId },
    }"
    >My Team</v-btn
  >
</template>

<script>
export default {
  props: {
    leagueId: {
      type: String,
      required: false,
    },
    userId: {
      type: String,
      required: false,
    },
  },
}
</script>
