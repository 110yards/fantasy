<template>
    <div>
        <v-simple-table>
            <template>
                <thead>
                    <tr>
                        <th>Passing</th>
                        <th>Comp.</th>
                        <th>ATT</th>
                        <th>Yards</th>
                        <th>TD</th>
                        <th>INT</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="player in inScope" :key="player.player_id">
                        <td>
                            <ReviewPlayer :season="season" :playerGame="player" />
                        </td>
                        <td>{{ player.stats.pass_completions }}</td>
                        <td>{{ player.stats.pass_attempts }}</td>
                        <td>{{ player.stats.pass_net_yards }}</td>
                        <td>{{ player.stats.pass_touchdowns }}</td>
                        <td>{{ player.stats.pass_interceptions }}</td>
                    </tr>
                </tbody>
            </template>
        </v-simple-table>
    </div>
</template>

<script>
import ReviewPlayer from "./ReviewPlayer.vue"

export default {
    name: "ReviewPassing",
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
            return this.players.filter((player) => player.stats.pass_attempts > 0).sort((a, b) => b.stats.pass_net_yards - a.stats.pass_net_yards)
        },
    }
}

</script>
