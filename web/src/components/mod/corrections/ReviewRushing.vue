<template>
  <div>
    <h3>Rushing</h3>
    <EditPlayerStats
      v-for="player in inScope"
      :key="player.player_id"
      :season="season"
      :text="getText(player)"
      :playerGame="player"
      @save="$emit('save')"
    />
  </div>
</template>

<script>
import EditPlayerStats from "./EditPlayerStats.vue"

export default {
  name: "ReviewRushing",
  components: { EditPlayerStats },
  props: {
    season: {
      type: Number,
      required: true,
    },
    players: {
      type: Array,
      required: true,
    },
  },
  computed: {
    inScope() {
      return this.players
        .filter(player => player.stats.rush_attempts > 0)
        .sort((a, b) => b.stats.rush_net_yards - a.stats.rush_net_yards)
    },
  },
  methods: {
    getText(player) {
      return `${player.stats.rush_attempts}-${player.stats.rush_net_yards} yds, ${player.stats.rush_touchdowns} TD`
    },
  },
}
</script>
