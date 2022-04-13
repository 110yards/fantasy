<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <p>Current Week: {{ currentWeek }}</p>
        <p>Waivers Active: {{ waiversActive }}</p>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="3" md="4">
        <app-default-button @click="updatePlayers">Update players</app-default-button>
      </v-col>

      <v-col cols="3" md="4">
        <app-default-button @click="updateGames">Update games</app-default-button>
        <v-container>
          <p>Simulate up to:</p>
          <app-select label="Game" :items="gameIds" v-model="gameId" />

          <app-select label="Quarter" :items="quarters" v-model="quarter" />
        </v-container>
      </v-col>

      <v-col cols="6" md="4">
        <app-default-button @click="endOfDay">End of Day</app-default-button>
        <br />
        <app-default-button class="mt-2" v-if="waiversActive" @click="resetWeekEnd">Reset week end</app-default-button>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { endOfDay, resetWeekEnd, updateGames, updatePlayers } from "../../api/110yards/admin"
import scoreboard from "../../mixins/scoreboard"
import eventBus from "../../modules/eventBus"
import AppDefaultButton from "../buttons/AppDefaultButton.vue"
import AppSelect from "../inputs/AppSelect.vue"
import AppTextField from "../inputs/AppTextField.vue"

export default {
  components: { AppDefaultButton, AppTextField, AppSelect },
  mixins: [scoreboard],

  data() {
    return {
      gameId: null,
      quarter: null,
    }
  },

  computed: {
    state() {
      return this.$root.state
    },

    currentWeek() {
      return this.state ? this.state.current_week : null
    },

    waiversActive() {
      return this.state ? this.state.waivers_active : null
    },

    gameIds() {
      let empty = [{ text: "(all)", value: null }]

      if (!this.scoreboard) return empty

      let ids = Object.keys(this.scoreboard.games)
      let items = ids.map(function (x) {
        return { text: x, value: x }
      })

      return [...empty, ...items]
    },

    quarters() {
      return [
        { text: "n/a", value: null },
        { text: "1", value: 1 },
        { text: "2", value: 2 },
        { text: "3", value: 3 },
        { text: "4", value: 4 },
      ]
    },

    waiversActive() {
      return this.$root.state.waivers_active
    },
  },

  methods: {
    async updatePlayers() {
      await updatePlayers()
      eventBus.$emit("show-info", "Players updated")
    },

    async updateGames() {
      let simState = {
        game_id: this.gameId,
        quarter: this.quarter,
      }

      await updateGames(simState)

      eventBus.$emit("show-info", "Games updated")
    },

    async endOfDay() {
      await endOfDay()

      eventBus.$emit("show-info", "End of day complete")
    },

    async resetWeekEnd() {
      await resetWeekEnd()
    },
  },
}
</script>
