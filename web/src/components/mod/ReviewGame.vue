<template>
  <v-card>
    <v-card-title> {{ game.away.location }} at {{ game.home.location }} </v-card-title>
    <v-card-subtitle>
      If you need to make corrections to the game data, you can do so here. Consider using the "Update source data"
      button to refresh the data from the source in case there is a correction that didn't get picked up prior to
      editing.
    </v-card-subtitle>
    <v-card-actions>
      <AppPrimaryButton @click="updateData">Update source data</AppPrimaryButton>
    </v-card-actions>

    <v-simple-table>
      <template>
        <tbody></tbody>
      </template>
    </v-simple-table>
  </v-card>
</template>

<script>
import { firestore } from "../../modules/firebase/index.js"
import AppDefaultButton from "../buttons/AppDefaultButton.vue"
import AppPrimaryButton from "../buttons/AppPrimaryButton.vue"
import AppTextField from "../inputs/AppTextField.vue"
import { updateGameData } from "../../api/110yards/mod.js"

export default {
  name: "Corrections",
  components: { AppPrimaryButton, AppDefaultButton, AppTextField },
  props: {
    game: {
      type: Object,
      required: true,
    },
    season: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      playerGames: null,
    }
  },
  computed: {},
  methods: {
    async updateData() {
      await updateGameData(this.game.game_id)
    },
  },
  watch: {
    game: {
      immediate: true,
      handler(v) {
        if (v) {
          let ref = firestore
            .collection(`season/${this.season}/player_games`)
            .where("game_id", "==", parseInt(v.game_id))

          this.$bind("playerGames", ref)
        }
      },
    },
  },
}
</script>
