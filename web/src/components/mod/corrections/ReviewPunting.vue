<template>
  <div>
    <h3>Punting</h3>
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
  name: "ReviewPunting",
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
        .filter(player => player.stats.punts > 0)
        .sort((a, b) => b.stats.punt_net_yards - a.stats.punt_net_yards)
    },
  },
  methods: {
    getText(player) {
      return `${player.stats.punts}-${player.stats.punt_gross_yards} yds, ${player.stats.punt_singles} singles`
    },
  },
}
</script>
