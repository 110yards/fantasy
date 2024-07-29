<template>
  <div>
    <h3>Receiving</h3>
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
  name: "ReviewReceiving",
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
        .filter(player => player.stats.receive_caught > 0)
        .sort((a, b) => b.stats.receive_yards - a.stats.receive_yards)
    },
  },
  methods: {
    getText(player) {
      return `${player.stats.receive_caught}-${player.stats.receive_yards} yds, ${player.stats.receive_touchdowns} TD`
    },
  },
}
</script>
