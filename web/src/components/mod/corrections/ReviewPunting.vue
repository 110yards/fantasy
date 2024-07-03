<template>
    <div>
        <v-simple-table>
            <template>
                <thead>
                    <tr>
                        <th>Punting</th>
                        <th>Punts</th>
                        <th>Yards</th>
                        <th>Singles</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="player in inScope" :key="player.player_id">
                        <td>
                            <ReviewPlayer :season="season" :playerGame="player" />
                        </td>
                        <td>{{ player.stats.punts }}</td>
                        <td>{{ player.stats.punt_net_yards }}</td>
                        <td>{{ player.stats.punt_singles }}</td>
                    </tr>
                </tbody>
            </template>
        </v-simple-table>
    </div>
</template>

<script>
import ReviewPlayer from "./ReviewPlayer.vue"

export default {
    name: "ReviewPunting",
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
            return this.players.filter((player) => player.stats.punts > 0).sort((a, b) => b.stats.punt_net_yards - a.stats.punt_net_yards)
        },
    }
}

</script>
