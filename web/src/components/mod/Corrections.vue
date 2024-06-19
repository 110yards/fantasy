<template>
  <div v-if="scoreboard">
    <v-simple-table v-if="!reviewGame">
      <template>
        <thead>
          <tr>
            <th>Date</th>
            <th>Game</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="game in scoreboard.games" :key="game.game_id">
            <td>{{ hoursAgo(game.date_start) }} hours ago</td>
            <td>{{ game.away.location }} at {{ game.home.location }}</td>
            <td>
              <AppPrimaryButton @click="reviewGame = game">Review</AppPrimaryButton>
            </td>
          </tr>
        </tbody>
      </template>
    </v-simple-table>
    <ReviewGame v-else :game="reviewGame" />
  </div>
</template>
  
<script>
import AppDefaultButton from "../buttons/AppDefaultButton.vue"
import AppPrimaryButton from "../buttons/AppPrimaryButton.vue"
import AppTextField from "../inputs/AppTextField.vue"
import ReviewGame from "./ReviewGame.vue"
import scoreboard from "../../mixins/scoreboard"

const minHoursToEdit = 72

export default {
  name: "Corrections",
  components: { AppPrimaryButton, AppDefaultButton, AppTextField, ReviewGame },
  mixins: [scoreboard],
  data() {
    return {
      reviewGame: null,
      playerGames: null,
      games: null,
      minHoursToEdit: minHoursToEdit,
    }
  },
  computed: {
    season() {
      return this.$root.state.current_season
    },
    weekNumber() {
      return this.$root.state.current_week
    },
  },
  methods: {
    hoursAgo(date) {
      const now = new Date()
      const diff = now - date.toDate()

      const hours = diff / 1000 / 60 / 60

      return Math.round(hours)
    },
    canEdit(game) {
      return this.hoursAgo(game.date_start) > minHoursToEdit
    },
    setupBindings() {
      if (!this.season || !this.weekNumber) return
    },
  },
}
</script>
