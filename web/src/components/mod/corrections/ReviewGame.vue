<template>
  <div>
    <h3>{{ game.away.location }} at {{ game.home.location }}</h3>
    <p class="text-subtitle">
      If you need to make corrections to the game data, you can do so here. Please use official sources to verify data.
    </p>
    <p>
      <AppPrimaryButton v-if="isAdmin" @click="updateData">Update source data</AppPrimaryButton>
      <AppDefaultButton @click="$emit('close')">Close Game</AppDefaultButton>
    </p>

    <v-tabs v-model="tab">
      <v-tab>{{ game.away.location }}</v-tab>
      <v-tab>{{ game.home.location }}</v-tab>

      <v-tabs-items v-model="tab">
        <v-tab-item>
          <v-card-text>
            <ReviewTeam :season="game.year" :players="awayPlayers" />
          </v-card-text>
        </v-tab-item>

        <v-tab-item>
          <v-card-text>
            <ReviewTeam :season="game.year" :players="homePlayers" />
          </v-card-text>
        </v-tab-item>
      </v-tabs-items>
    </v-tabs>
  </div>
</template>

<style scoped></style>

<script>
import { firestore } from "../../../modules/firebase/index.js"
import AppDefaultButton from "../../buttons/AppDefaultButton.vue"
import AppPrimaryButton from "../../buttons/AppPrimaryButton.vue"
import AppTextField from "../../inputs/AppTextField.vue"
import { updateGameData } from "../../../api/110yards/mod.js"
import ReviewTeam from "./ReviewTeam.vue"

export default {
  name: "ReviewGame",
  components: { AppPrimaryButton, AppDefaultButton, AppTextField, ReviewTeam },
  emit: ["close"],
  props: {
    game: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      playerGames: null,
      tab: "away",
    }
  },
  computed: {
    isAdmin() {
      return this.$root.isAdmin
    },

    awayPlayers() {
      return this.playerGames.filter(pg => pg.team.abbr == this.game.away.abbr)
    },

    homePlayers() {
      return this.playerGames.filter(pg => pg.team.abbr == this.game.home.abbr)
    },
  },
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
          // console.log(`season/${v.year}/player_game where game_id == ${v.game_id}`)
          let ref = firestore
            .collection("season")
            .doc(`${v.year}`)
            .collection("player_game")
            .where("game_id", "==", parseInt(v.game_id))

          this.$bind("playerGames", ref)
        }
      },
    },
  },
}
</script>
