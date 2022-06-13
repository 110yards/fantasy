<template>
  <v-row class="spot mb-1">
    <!-- Receive and drop actions, desktop -->
    <v-col cols="0" md="1" class="d-none d-md-block">
      <span v-if="playerToBeMoved && playerToBeMoved == spot.player">
        <v-icon @click="$emit('confirmDrop', spot)">mdi-minus</v-icon>
      </span>
      <span v-if="canReceive">
        <v-icon @click="$emit('acceptPlayer', spot)">mdi-arrow-right-bold</v-icon>
      </span>
    </v-col>
    <!-- / Receive and drop, desktop -->

    <!-- Position, both -->
    <v-col cols="2" md="1">
      <span v-if="!playerToBeMoved || playerToBeMoved != spot.player">
        <v-btn
          class="ml-n2 mt-n2"
          icon
          text
          :title="spot.name"
          :outlined="canEdit && !isLocked"
          :class="isLocked ? 'nohand' : canEdit ? 'blue--text' : 'nohand'"
          @click="canEdit ? $emit('movePlayer', spot) : null"
          >{{ name }}</v-btn
        >
      </span>

      <span v-if="playerToBeMoved && playerToBeMoved == spot.player && !isLocked">
        <v-btn @click="$emit('cancelMovePlayer')" class="ml-n2 mt-n2" icon text :title="spot.name" outlined>
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </span>
    </v-col>
    <!-- / Position, both -->

    <!-- Player -->
    <v-col cols="7">
      <v-row v-if="spot.player">
        <player-link
          :player="spot.player"
          :leagueId="leagueId"
          :showTeamLogo="true"
          :showTeamName="false"
          :shortenName="false"
          :showPosition="true"
          :showPlayerStatus="true"
        />
      </v-row>
      <!-- todo: max name length -->

      <v-row>
        <span v-if="spot.player && scoreboard"><game-state :player="spot.player" :scoreboard="scoreboard" /></span>
      </v-row>
      <!-- could I get some stats in here? -->
    </v-col>
    <!-- /Player -->

    <!-- score, desktop -->
    <v-col cols="0" md="3" class="text-right d-none d-md-block">
      <v-row>
        <v-col class="py-0">
          <position-score :leagueId="leagueId" :position="spot" :scoreboard="scoreboard" :weekNumber="weekNumber" />
        </v-col>
      </v-row>
      <v-row v-if="playerScore && enableProjections">
        <v-col class="py-0 caption grey--text"><score :score="projection" /></v-col>
      </v-row>

      <v-row v-if="playerToBeMoved">
        <span v-if="playerToBeMoved == spot.player"> </span>

        <span v-if="canReceive"> </span>
      </v-row>
    </v-col>
    <!-- /score, desktop -->

    <!-- score, drop and receive actions, mobile -->
    <v-col cols="3" md="0" class="text-right d-block d-md-none">
      <v-row>
        <v-col v-if="!playerToBeMoved" class="py-0">
          <span v-if="gameStarted">
            <position-score :leagueId="leagueId" :position="spot" :scoreboard="scoreboard" :weekNumber="weekNumber" />
          </span>
          <span v-else>--</span>
        </v-col>

        <v-col v-if="playerToBeMoved">
          <span v-if="playerToBeMoved && playerToBeMoved == spot.player">
            <v-icon @click="$emit('confirmDrop', spot)">mdi-minus</v-icon>
          </span>
          <span v-if="canReceive">
            <v-icon @click="$emit('acceptPlayer', spot)">mdi-arrow-left-bold</v-icon>
          </span>
        </v-col>
      </v-row>
      <v-row v-if="!playerToBeMoved && playerScore && enableProjections">
        <v-col class="py-0 caption grey--text"><score :score="projection" /></v-col>
      </v-row>

      <v-row v-if="playerToBeMoved">
        <span v-if="playerToBeMoved == spot.player"> </span>

        <span v-if="canReceive"> </span>
      </v-row>
    </v-col>
    <!-- /score, drop and receive actions, mobile -->
  </v-row>
</template>

<style scoped>
.nohand {
  pointer-events: none;
}

.spot {
  border-bottom: 1px solid black;
}
</style>

<script>
import PlayerLink from "../../player/PlayerLink.vue"
import Locked from "../../icons/Locked.vue"
import { eventStatus, playerStatus, positionType, teamId } from "../../../api/110yards/constants"
import NationalStatus from "../../player/NationalStatus.vue"
import GameState from "../GameState.vue"
import { firestore } from "../../../modules/firebase"
import PositionScore from "../PositionScore.vue"
import Score from "../../Score.vue"

export default {
  name: "lineup-spot",
  components: {
    PlayerLink,
    Locked,
    NationalStatus,
    GameState,
    PositionScore,
    Score,
  },
  props: {
    spot: {
      type: Object,
      required: true,
    },
    canEdit: {
      type: Boolean,
      required: false,
      default: false,
    },
    leagueId: String,
    playerToBeMoved: {
      type: Object,
      required: false,
    },
    scoreboard: {
      type: Object,
      required: false,
    },
    active: {
      type: Boolean,
      required: true,
    },
  },

  data() {
    return {
      playerScore: null,
    }
  },

  computed: {
    enableProjections() {
      return this.$root.enableProjections
    },

    projection() {
      if (!this.spot.player || !this.playerScore) return

      if (this.spot.player.team.id == teamId.FreeAgent) return 0

      if (this.$root.getOpponent(this.spot.player.team.abbreviation) == "FA") return 0

      return this.playerScore.average_score
    },
    name() {
      return positionType.spotName(this.spot.position_type)
    },
    isReserveSpot() {
      return this.$root.isReservePositionType(this.spot.position_type)
    },

    isLocked() {
      return !!this.spot.player && this.$root.isLocked(this.spot.player.team.abbreviation)
    },

    positionsForSpot() {
      return this.$root.eligiblePlayerPositions(this.spot.position_type)
    },

    playerToBeMovedIsSame() {
      return !!this.playerToBeMoved && !!this.spot.player && this.playerToBeMoved.id == this.spot.player.id
    },

    canReceive() {
      return (
        this.playerToBeMoved &&
        !this.playerToBeMovedIsSame &&
        this.$root.playerIsEligibleForPosition(this.playerToBeMoved, this.spot.position_type, true)
      )
    },

    statusText() {
      if (!this.spot.player) return null

      return playerStatus.getText(this.spot.player.status_current)
    },

    game() {
      if (!this.spot.player) return null

      return this.$root.getGameForTeam(this.spot.player.team.abbreviation, this.scoreboard)
    },

    gameStarted() {
      if (!this.game) return false
      return [eventStatus.InProgress, eventStatus.Final].includes(this.game.event_status.event_status_id)
    },

    weekNumber() {
      return this.$root.state.current_week
    },
  },

  methods: {
    configureReferences() {
      if (!this.leagueId || !this.spot || !this.spot.player) return

      let ref = firestore.doc(`league/${this.leagueId}/player_score/${this.spot.player.id}`)
      this.$bind("playerScore", ref)
    },
  },

  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        if (!leagueId) return

        this.configureReferences()
      },
    },

    spot: {
      immediate: true,
      handler(spot) {
        if (!spot) return

        this.configureReferences()
      },
    },
  },
}
</script>
