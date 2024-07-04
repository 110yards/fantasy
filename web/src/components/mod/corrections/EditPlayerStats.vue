<template>
    <v-container v-if="editedStats">
        <v-row>
            <h2>Passing</h2>
        </v-row>
        <v-row>
            <v-col cols="6" md="2">
                <AppTextField :value="`${editedStats.pass_attempts}`"
                    @input="(value) => editedStats.pass_attempts = value" label="Attempts" />
            </v-col>
            <v-col cols="6" md="2">
                <AppTextField :value="`${editedStats.pass_completions}`"
                    @input="(value) => editedStats.pass_completions = value" label="Completions" />
            </v-col>
            <AppTextField :value="`${editedStats.pass_net_yards}`"
                @input="(value) => editedStats.pass_net_yards = value" label="Net Yards" />
            <AppTextField :value="`${editedStats.pass_touchdowns}`"
                @input="(value) => editedStats.pass_touchdowns = value" label="Touchdowns" />
            <AppTextField :value="`${editedStats.pass_interceptions}`"
                @input="(value) => editedStats.pass_interceptions = value" label="Interceptions" />
        </v-row>
        <v-col cols="12" md="6">
            <h2>Rushing</h2>
            <AppTextField :value="`${editedStats.rush_attempts}`" @input="(value) => editedStats.rush_attempts = value"
                label="Attempts" />
            <AppTextField :value="`${editedStats.rush_net_yards}`"
                @input="(value) => editedStats.rush_net_yards = value" label="Net Yards" />
            <AppTextField :value="`${editedStats.rush_touchdowns}`"
                @input="(value) => editedStats.rush_touchdowns = value" label="Touchdowns" />
        </v-col>


        <AppPrimaryButton @click="save">Save</AppPrimaryButton>
        <AppDefaultButton class="ml-2" @click="$emit('close')">Cancel</AppDefaultButton>
    </v-container>

</template>

<script>
import AppTextField from "../../inputs/AppTextField.vue"
import AppPrimaryButton from "../../buttons/AppPrimaryButton.vue"
import AppDefaultButton from "../../buttons/AppDefaultButton.vue";

export default {
    name: "EditPlayerStats",
    components: { AppTextField, AppPrimaryButton, AppDefaultButton },
    props: {
        playerStats: {
            type: Object,
            required: true,
        },
    },
    data() {
        return {
            editedStats: this.playerStats,
        }
    },
    methods: {
        async save() {
            this.$emit("save", this.playerStats)
        },
    },
}


</script>
