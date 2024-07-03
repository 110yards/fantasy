<template>
    <div>
        <v-simple-table>
            <template>
                <thead>
                    <tr>
                        <th>Receiving</th>
                        <th>Rec</th>
                        <th>Yards</th>
                        <th>TD</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="player in inScope" :key="player.player_id">
                        <td>
                            <ReviewPlayer :season="season" :playerGame="player" />
                        </td>
                        <td>{{ player.stats.receive_caught }}</td>
                        <td>{{ player.stats.receive_yards }}</td>
                        <td>{{ player.stats.receive_touchdowns }}</td>
                    </tr>
                </tbody>
            </template>
        </v-simple-table>
    </div>
</template>

<script>
import ReviewPlayer from "./ReviewPlayer.vue"

export default {
    name: "ReviewReceiving",
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
            return this.players.filter((player) => player.stats.receive_caught > 0).sort((a, b) => b.stats.receive_yards - a.stats.receive_yards)
        },
    }
}

</script>
