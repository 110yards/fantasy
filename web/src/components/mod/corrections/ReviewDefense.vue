<template>
    <div>
        <v-simple-table>
            <template>
                <thead>
                    <tr>
                        <th>Defense</th>
                        <th>DT</th>
                        <th>STT</th>
                        <th>Sacks</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="player in inScope" :key="player.player_id">
                        <td>
                            <ReviewPlayer :season="season" :playerGame="player" />
                        </td>
                        <td>{{ player.stats.tackles_defensive }}</td>
                        <td>{{ player.stats.tackles_special_teams }}</td>
                        <td>{{ player.stats.sacks_qb_made }}</td>
                    </tr>
                </tbody>
            </template>
        </v-simple-table>
    </div>
</template>

<script>
import ReviewPlayer from "./ReviewPlayer.vue"

export default {
    name: "ReviewDefense",
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
            return this.players.filter((player) => player.stats.tackles_defensive > 0 || player.stats.tackles_special_teams).sort((a, b) => b.stats.tackles_defensive - a.stats.tackles_defensive)
        },
    }
}

</script>
