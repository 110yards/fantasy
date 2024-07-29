<template>
    <div>
        <h3>Kicking</h3>
        <EditPlayerStats v-for="player in inScope" :key="player.player_id" :season="season" :text="getText(player)"
            :playerGame="player" @save="$emit('save')" />
    </div>
</template>

<script>
import EditPlayerStats from "./EditPlayerStats.vue"

export default {
    name: "ReviewKicking",
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
            return this.players.filter((player) => player.stats.field_goal_attempts > 0 || player.stats.one_point_converts_attempts > 0).sort((a, b) => b.stats.field_goal_made - a.stats.field_goal_made)
        },
    },
    methods: {
        getText(player) {
            return `${player.stats.field_goal_made}/${player.stats.field_goal_attempts} FGM, ${player.stats.one_point_converts_made}/${player.stats.one_point_converts_attempts} XP, ${player.stats.field_goal_singles} singles`
        }
    }
}

</script>
