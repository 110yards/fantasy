<template>
  <span v-if="player" class="player" :data-player-id="player.id">
    <!-- left to right -->
    <template v-if="!reverse">
      <span v-if="showTeamLogo" class="team-icon" :class="team"> </span>
      <router-link
        v-if="enablePlayerLinks"
        :to="{ name: 'league-player', params: { leagueId: leagueId, playerId: player.id } }"
      >
        {{ displayName }}
      </router-link>
      <span v-else :class="playerNameClass">
        {{ displayName }}
      </span>

      <span v-if="showTeamName" class="pl-1">{{ player.team.abbreviation }}</span>
      <span v-if="showPosition" class="pl-1">&nbsp;- {{ player.position.toUpperCase() }}</span>

      <span class="red--text pl-1" v-if="showPlayerStatus">
        {{ statusText }}
      </span>

      <v-icon v-if="showShortPlayerStatus && isInjured" color="red" small>mdi-hospital</v-icon>

      <national-status v-if="showNational" :national_status="player.national_status" />
    </template>

    <!-- right to left -->
    <template v-else>
      <national-status v-if="showNational" :national_status="player.national_status" />

      <v-icon v-if="showShortPlayerStatus && isInjured" color="red" small>mdi-hospital</v-icon>
      <span class="red--text" v-if="showPlayerStatus">
        {{ statusText }}
      </span>

      <router-link
        v-if="enablePlayerLinks"
        :to="{ name: 'league-player', params: { leagueId: leagueId, playerId: player.id } }"
      >
        {{ displayName }}
      </router-link>
      <span v-else :class="playerNameClass">
        {{ displayName }}
      </span>

      <span v-if="showTeamName" class="">{{ player.team.abbreviation }}</span>
      <span v-if="showPosition" class="">&nbsp;- {{ player.position.toUpperCase() }}</span>

      <span v-if="showTeamLogo" class="team-icon pl-1" :class="team"> </span>
    </template>
  </span>
</template>

<style scoped></style>

<script>
import { playerStatus } from "../../api/110yards/constants"
import NationalStatus from "./NationalStatus.vue"
import PlayerStatus from "./PlayerStatus.vue"

export default {
  name: "player-link",
  components: {
    PlayerStatus,
    NationalStatus,
  },
  props: {
    leagueId: {
      required: true,
      type: String,
    },
    player: {
      required: false,
      type: Object,
    },
    showTeamLogo: {
      required: false,
      type: Boolean,
      default: true,
    },
    reverse: {
      required: false,
      type: Boolean,
      default: false,
    },
    showStatus: {
      required: false,
      type: Boolean,
      default: true,
    },
    showNational: {
      required: false,
      type: Boolean,
      default: true,
    },
    shortenName: {
      required: false,
      type: Boolean,
      default: false,
    },
    showTeamName: {
      required: false,
      type: Boolean,
      default: false,
    },
    showPosition: {
      required: false,
      type: Boolean,
      default: false,
    },
    boldName: { required: false, type: Boolean, default: false },
    maxNameLength: { required: false, type: Number, default: null },
    showShortPlayerStatus: { required: false, type: Boolean, default: false },
  },
  computed: {
    playerNameClass() {
      return this.boldName ? "font-weight-bold" : ""
    },
    team() {
      return this.player.team != null ? this.player.team.abbreviation : "FA"
    },
    showPlayerStatus() {
      return this.showStatus && this.status != playerStatus.Active
    },
    isInjured() {
      return this.status != playerStatus.Active
    },
    status() {
      return this.player.status_current
    },
    statusText() {
      return playerStatus.getText(this.status)
    },
    enablePlayerLinks() {
      return this.$root.enablePlayerLinks
    },
    shortName() {
      return `${this.player.first_name[0]}. ${this.player.last_name}`
    },
    displayName() {
      let name = this.shortenName ? this.shortName : this.player.display_name

      if (this.maxNameLength && name.length > this.maxNameLength) {
        return `${name.substring(0, this.maxNameLength)}...`
      } else {
        return name
      }
    },
  },
}
</script>