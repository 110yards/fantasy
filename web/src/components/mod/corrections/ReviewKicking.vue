<template>
    <div>
        <v-simple-table>
            <template>
                <thead>
                    <tr>
                        <th>Kicking</th>
                        <th>FG Made</th>
                        <th>FG Miss</th>
                        <th>Miss (Single)</th>
                        <th>Convert</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="player in inScope" :key="player.player_id">
                        <td>
                            <ReviewPlayer :season="season" :playerGame="player" />
                        </td>
                        <td>{{ player.stats.field_goal_made }}</td>
                        <td>{{ player.stats.field_goal_misses }}</td>
                        <td>{{ player.stats.field_goal_singles }}</td>
                        <td>{{ player.stats.one_point_converts_made }}</td>
                    </tr>
                </tbody>
            </template>
        </v-simple-table>
    </div>
</template>

<script>
import ReviewPlayer from "./ReviewPlayer.vue"

export default {
    name: "ReviewKicking",
    components: { ReviewPlayer },
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
    }
}

</script>
