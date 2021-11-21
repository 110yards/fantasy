<template>
  <v-btn text class="nav-item nav-link" :to="{ name: 'league-players', params: { leagueId: leagueId } }">Players</v-btn>
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
