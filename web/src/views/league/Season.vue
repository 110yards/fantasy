<template>
  <div>
    <season-summary :leagueId="leagueId" :season="seasonId" />
  </div>
</template>

<script>
import SeasonSummary from "../../components/league/SeasonSummary.vue"

export default {
  components: {
    SeasonSummary,
  },

  props: {
    leagueId: { type: String, required: true },
    seasonId: {
      type: String,
      required: true,
    },
  },
}
</script>
