<template>
    <div>
        <h3>Passing</h3>
        <EditPlayerStats v-for="player in inScope" :key="player.player_id" :season="season" :text="getText(player)"
            :playerGame="player" @save="$emit('save')" />
    </div>
</template>

<script>
import EditPlayerStats from "./EditPlayerStats.vue"

export default {
    name: "ReviewPassing",
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

    data() {
        return {
            editPlayer: null,
        }
    },

    computed: {
        inScope() {
            return this.players.filter((player) => player.stats.pass_attempts > 0).sort((a, b) => b.stats.pass_net_yards - a.stats.pass_net_yards)
        },
    },

    methods: {
        getText(player) {
            return `${player.stats.pass_completions} / ${player.stats.pass_attempts}, ${player.stats.pass_net_yards} yds, ${player.stats.pass_touchdowns} TD, ${player.stats.pass_interceptions} INT`
        }
    }
}

</script>
