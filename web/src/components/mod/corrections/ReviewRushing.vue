<template>
    <div>
        <v-simple-table>
            <template>
                <thead>
                    <tr>
                        <th>Rushing</th>
                        <th>ATT</th>
                        <th>Yards</th>
                        <th>TD</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="player in inScope" :key="player.player_id">
                        <td>
                            <ReviewPlayer :season="season" :playerGame="player" />
                        </td>
                        <td>{{ player.stats.rush_attempts }}</td>
                        <td>{{ player.stats.rush_net_yards }}</td>
                        <td>{{ player.stats.rush_touchdowns }}</td>
                    </tr>
                </tbody>
            </template>
        </v-simple-table>
    </div>
</template>

<script>
import ReviewPlayer from "./ReviewPlayer.vue"

export default {
    name: "ReviewRushing",
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
            return this.players.filter((player) => player.stats.rush_attempts > 0).sort((a, b) => b.stats.rush_net_yards - a.stats.rush_net_yards)
        },
    }
}

</script>
