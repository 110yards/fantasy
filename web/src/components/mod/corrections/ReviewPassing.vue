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
                        <th></th>
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
                        <td>
                            <AppPrimaryButton text @click="editPlayer = player.stats">Edit</AppPrimaryButton>
                        </td>
                    </tr>
                    <tr>
                        <td colspan="7">
                            <EditPlayerStats v-if="editPlayer" :playerStats="editPlayer" @save="$emit('save')"
                                @cancel="editPlayer = null" />
                        </td>
                    </tr>

                </tbody>
            </template>
        </v-simple-table>
    </div>
</template>

<script>
import AppPrimaryButton from "../../buttons/AppPrimaryButton.vue";
import AppTextField from "../../inputs/AppTextField.vue";
import ReviewPlayer from "./ReviewPlayer.vue"
import EditPlayerStats from "./EditPlayerStats.vue"

export default {
    name: "ReviewPassing",
    components: { ReviewPlayer, AppPrimaryButton, AppTextField, EditPlayerStats },
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
    }
}

</script>
