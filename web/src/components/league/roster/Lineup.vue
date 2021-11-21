<template>
  <v-container class="lineup">
    <v-alert v-if="showNewRosterUITip && !confirming" outlined dense type="info" class="caption"
      >Move and drop players by clicking the position button on the left</v-alert
    >

    <v-col cols="12" v-if="confirming">
      <p>{{ confirmMessage }}</p>

      <app-primary-button class="mr-2" @click="cancelConfirmation()">No</app-primary-button>
      <app-default-button class="mr-2" @click="confirmAction">Yes, do it</app-default-button>
    </v-col>

    <template v-if="positions && !confirming">
      <lineup-spot
        :class="spot.position_type"
        v-for="spot in sortedSpots"
        :key="spot.id"
        :spot="spot"
        :leagueId="leagueId"
        :player="spot.player"
        :canEdit="canEdit"
        :playerToBeMoved="playerToBeMoved"
        v-on:confirmDrop="confirmDropPlayer"
        v-on:movePlayer="showMoveTargets"
        v-on:acceptPlayer="movePlayer"
        v-on:cancelMovePlayer="cancelMovePlayer"
        :scoreboard="scoreboard"
      />

      <!-- <lineup-spot-mobile
        class="d-md-none"
        :class="spot.active ? 'active' : ''"
        v-for="spot in sortedSpots"
        :key="'m' + spot.id"
        :spot="spot"
        :leagueId="leagueId"
        :player="spot.player"
        :canEdit="canEdit"
        :playerToBeMoved="playerToBeMoved"
        v-on:confirmDrop="confirmDropPlayer"
        v-on:movePlayer="showMoveTargets"
        v-on:acceptPlayer="movePlayer"
        v-on:cancelMovePlayer="cancelMovePlayer"
      /> -->
    </template>
  </v-container>
</template>

<style scoped>
/* .spot.active:last-child() {
  
  border-bottom: 1px solid red;
} */
</style>

<script>
// import LineupSpotDesktop from "./LineupSpotDesktop.vue"
import * as formatter from "../../../modules/formatter"
import AppPrimaryButton from "../../buttons/AppPrimaryButton.vue"
import AppDefaultButton from "../../buttons/AppDefaultButton.vue"
import { dropPlayer, movePlayer } from "../../../api/110yards/roster"
import { draftState } from "../../../api/110yards/constants"
// import LineupSpotMobile from "./LineupSpotMobile.vue"
import LineupSpot from "./LineupSpot.vue"
import scoreboard from "../../../mixins/scoreboard"

export default {
  name: "lineup",
  components: {
    // LineupSpotDesktop,
    AppPrimaryButton,
    AppDefaultButton,
    // LineupSpotMobile,
    LineupSpot,
  },
  mixins: [scoreboard],
  props: {
    roster: {
      type: Object,
      required: true,
    },
    league: {
      type: Object,
      required: true,
    },
    canEdit: {
      type: Boolean,
      required: false,
      default: false,
    },
  },

  data() {
    return {
      confirming: false,
      confirmMessage: null,
      confirmAction: null,
      playerToBeMoved: null,
    }
  },

  computed: {
    showNewRosterUITip() {
      return this.$root.showNewRosterUITip
    },
    leagueId() {
      return this.league.id
    },
    positions() {
      let useLeaguePositions = this.league && this.league.draft_state != draftState.Complete
      let useRosterPositions = this.roster && !this.useLeaguePositions

      if (useLeaguePositions) {
        console.debug("League not ready, showing default league positions")
        return Object.values(this.league.positions)
      }

      if (useRosterPositions) {
        console.debug("League ready, showing roster positions")
        return Object.values(this.roster.positions)
      }

      console.warn("No roster positions available")
      return null
    },

    sortedSpots() {
      if (this.positions.length == 0) return null
      let active = this.positions.filter(spot => this.$root.isActivePositionType(spot.position_type))
      for (let x of active) {
        x.active = true
      }

      let bench = this.positions.filter(spot => this.$root.isBenchPositionType(spot.position_type))
      let reserve = this.positions.filter(spot => this.$root.isReservePositionType(spot.position_type))

      return active.concat(bench).concat(reserve)
    },
  },
  methods: {
    formatScore(score) {
      if (score == null || score == undefined) score = 0

      return formatter.formatScore(score)
    },

    confirmDropPlayer(spot) {
      this.confirmMessage = `Drop ${spot.player.display_name}?`
      this.confirming = true
      this.confirmAction = async () => {
        let command = {
          league_id: this.league.id,
          roster_id: this.roster.id,
          player_id: spot.player.id,
        }

        await dropPlayer(command)

        this.playerToBeMoved = null
        this.confirming = false
      }
    },

    cancelConfirmation() {
      this.cancelMovePlayer()
      this.confirmMessage = null
      this.confirming = false
    },

    showMoveTargets(spot) {
      this.playerToBeMoved = spot.player
    },

    async movePlayer(spot) {
      let command = {
        league_id: this.league.id,
        roster_id: this.roster.id,
        player_id: this.playerToBeMoved.id,
        position_id: spot.id,
      }

      await movePlayer(command)

      this.playerToBeMoved = null
    },

    cancelMovePlayer() {
      this.playerToBeMoved = null
    },
  },
}
</script>
