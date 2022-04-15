<template>
  <div>
    <v-alert dense type="info" v-if="waiversActive">
      Waivers are active, so you must bid on this player. Bids of $0 are allowed.
    </v-alert>
    <v-alert dense type="warning" v-if="!canAddWithoutDrop">
      You have no roster space for this player, you must choose a player to drop
      <span v-if="waiversActive">if your bid is successful</span>
    </v-alert>

    <h3>Add player</h3>
    <v-col cols="2" v-if="waiversActive">
      <v-form ref="bidForm">
        <app-number-field
          v-model="bid"
          required
          label="Waiver bid"
          min="0"
          prependInnerIcon="mdi-currency-usd"
          :rules="bidRules"
          :max="currentRoster.waiver_budget.toString()"
        />
      </v-form>
    </v-col>

    <v-simple-table>
      <template>
        <thead>
          <tr>
            <th></th>
            <th></th>
            <th>Player</th>
            <th>Opp</th>
            <th>Pos</th>
            <th>GP</th>
            <th>Rk</th>
            <th>Points</th>
            <th>Avg</th>
          </tr>
        </thead>

        <tbody>
          <tr>
            <td colspan="2"><app-primary-button @click="$emit('cancel')">Cancel</app-primary-button></td>
            <td><player-link :player="player" :leagueId="leagueId" /></td>
            <td>{{ getNextOpponent(player) }}</td>
            <td>{{ player.position.toUpperCase() }}</td>
            <td></td>
            <td></td>
            <td>{{ getSeasonPoints(player) }}</td>
            <td></td>
          </tr>

          <tr>
            <td colspan="9"></td>
          </tr>

          <tr>
            <th colspan="9">Drop player</th>
          </tr>

          <tr v-if="canAddWithoutDrop">
            <td colspan="9">
              <app-primary-button @click="confirmAddPlayer()">
                Don't drop anyone (roster is not full)
              </app-primary-button>
            </td>
          </tr>

          <tr v-for="spot in dropTargets" :key="spot.id">
            <td>
              <app-primary-button @click="confirmAddPlayer(spot)" v-if="!canAddWithoutDrop">Drop</app-primary-button>
              <app-default-button @click="confirmAddPlayer(spot)" v-if="canAddWithoutDrop">Drop</app-default-button>
            </td>
            <td>{{ spot.name }}</td>
            <td><player-link :player="spot.player" :leagueId="leagueId" /></td>
            <td>{{ getNextOpponent(spot.player) }}</td>
            <td>{{ spot.player.position.toUpperCase() }}</td>
            <td></td>
            <td></td>
            <td>{{ getSeasonPoints(spot.player) }}</td>
            <td></td>
          </tr>
        </tbody>
      </template>
    </v-simple-table>
  </div>
</template>

<script>
import { addPlayer } from "../../api/110yards/roster"
import eventBus from "../../modules/eventBus"
import { formatScore } from "../../modules/formatter"
import AppDefaultButton from "../buttons/AppDefaultButton.vue"
import AppPrimaryButton from "../buttons/AppPrimaryButton.vue"
import AppNumberField from "../inputs/AppNumberField.vue"
import AppTextField from "../inputs/AppTextField.vue"
import ComparePlayerTable from "./ComparePlayerTable.vue"
import PlayerLink from "./PlayerLink.vue"
export default {
  components: { ComparePlayerTable, PlayerLink, AppPrimaryButton, AppDefaultButton, AppNumberField },
  name: "AddPlayer",
  AppTextField,

  props: {
    waiversActive: { type: Boolean, required: true },
    currentRoster: { type: Object, required: true },
    leagueId: { type: String, required: true },
    player: { type: Object, required: true },
    playerScores: { type: Array, required: true },
  },

  data() {
    return {
      bid: null,
      bidRules: [v => (v !== "" && parseInt(v) >= 0) || "A bid is required"],
    }
  },

  computed: {
    dropTargets() {
      if (this.currentRoster == null) return []

      let positions = Object.values(this.currentRoster.positions)
      let eligibleDropPositions = positions.filter(
        p => p.player != null && this.$root.playerIsEligibleForPosition(this.player, p.position_type),
      )

      return eligibleDropPositions
    },

    canAddWithoutDrop() {
      if (this.currentRoster == null) return []

      let positions = Object.values(this.currentRoster.positions)

      let eligibleEmptyPositions = positions.filter(
        p => p.player == null && this.$root.playerIsEligibleForPosition(this.player, p.position_type, false),
      )

      console.debug(eligibleEmptyPositions)

      return eligibleEmptyPositions.length >= 1
    },
  },

  methods: {
    getNextOpponent(player) {
      return player != null && player.team != null ? this.$root.getOpponent(player.team.abbreviation) : ""
    },

    getSeasonPoints(player) {
      let filterResults = this.playerScores.filter(p => p.id == player.id)

      let playerScore = filterResults && filterResults.length == 1 ? filterResults[0] : null

      return playerScore != null && playerScore.season_score ? formatScore(playerScore.season_score.total_score) : ""
    },

    isLocked(player) {
      return this.$root.isLocked(player.team.abbreviation)
    },

    async confirmAddPlayer(dropTarget) {
      if (this.waiversActive) {
        let valid = await this.$refs.bidForm.validate()
        if (!valid) {
          eventBus.$emit("show-error", "A bid is required while waivers are active")
          return
        }
      }

      let command = {
        league_id: this.leagueId,
        roster_id: this.currentRoster.id,
        player_id: this.player.id,
        drop_player_id: dropTarget != null ? dropTarget.player.id : null,
        bid: this.bid,
      }

      let result = await addPlayer(command)

      if (result.success) {
        let inputPage = this.waiversActive ? "waivers" : "roster"

        this.$router.push({
          name: "roster",
          params: { leagueId: this.leagueId, rosterId: this.currentRoster.id, inputPage: inputPage },
        })
      }
    },
  },
}
</script>
