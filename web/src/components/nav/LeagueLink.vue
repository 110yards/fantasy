<template>
  <v-btn text class="nav-item nav-link" :to="{ name: 'league', params: { leagueId: leagueId } }">League</v-btn>
</template>

<script>
export default {
  props: {
    leagueId: {
      type: String,
      required: false,
    },
  },
}
</script>
