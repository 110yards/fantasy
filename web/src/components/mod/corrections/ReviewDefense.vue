<template>
  <div>
    <h3>Defense</h3>
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
  name: "ReviewDefense",
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
        .filter(player => player.stats.tackles_defensive > 0 || player.stats.tackles_special_teams)
        .sort((a, b) => b.stats.tackles_defensive - a.stats.tackles_defensive)
    },
  },
  methods: {
    getText(player) {
      return `${player.stats.tackles_defensive} tkl, ${player.stats.tackles_special_teams} stt, ${player.stats.sacks_qb_made} sacks, ${player.stats.interceptions} INT, ${player.stats.fumbles_recovered} FR`
    },
  },
}
</script>
