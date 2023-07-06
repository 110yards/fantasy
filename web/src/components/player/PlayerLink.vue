<template>
  <span v-if="player" class="player" :data-player-id="player.player_id">
    <!-- left to right -->
    <template v-if="!reverse">
      <span v-if="showTeamLogo" class="team-icon" :class="team"> </span>
      <router-link
        v-if="enablePlayerLinks"
        :to="{ name: 'league-player', params: { leagueId: leagueId, playerId: player.player_id } }"
      >
        {{ displayName }}
      </router-link>
      <span v-else :class="playerNameClass">
        {{ displayName }}
      </span>

      <span v-if="showTeamName" class="pl-1">{{ player.team_abbr }}</span>
      <span v-if="showPosition" class="pl-1">&nbsp;- {{ player.position.toUpperCase() }}</span>

      <span
        class="pl-1"
        :class="injuryTextColor"
        v-if="showPlayerStatus && !showShortPlayerStatus"
        :title="injuryDetails"
      >
        {{ injuryReport }}
      </span>

      <v-icon v-if="showShortPlayerStatus && isInjured" :color="injuryIconColor" small>{{ injuryIcon }}</v-icon>

      <canadian-status v-if="showCanadian" :isCanadian="player.canadian_player" />
    </template>

    <!-- right to left -->
    <template v-else>
      <canadian-status v-if="showCanadian" :isCanadian="player.canadian_player" />

      <v-icon v-if="showShortPlayerStatus && isInjured" :color="injuryIconColor" small>{{ injuryIcon }}</v-icon>
      <span :class="injuryTextColor" v-if="showPlayerStatus && !showShortPlayerStatus" :title="injuryDetails">
        {{ injuryReport }}
      </span>

      <router-link
        v-if="enablePlayerLinks"
        :to="{ name: 'league-player', params: { leagueId: leagueId, playerId: player.player_id } }"
      >
        {{ displayName }}
      </router-link>
      <span v-else :class="playerNameClass">
        {{ displayName }}
      </span>

      <span v-if="showTeamName" class="">{{ player.team_abbr }}</span>
      <span v-if="showPosition" class="">&nbsp;- {{ player.position.toUpperCase() }}</span>

      <span v-if="showTeamLogo" class="team-icon pl-1" :class="team"> </span>
    </template>
  </span>
</template>

<style scoped></style>

<script>
import { playerStatus } from "../../api/110yards/constants"
import CanadianStatus from "./CanadianStatus.vue"

export default {
  name: "player-link",
  components: {
    CanadianStatus,
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
    showCanadian: {
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
      return this.player.team_abbr ? this.player.team_abbr.toUpperCase() : "FA"
    },
    showPlayerStatus() {
      return this.isInjured
    },
    isInjured() {
      return !!this.player["injury_status"] || false
    },
    injuryStatus() {
      return this.player.injury_status
    },
    statusText() {
      if (!this.isInjured) {
        return null
      }
      return playerStatus.getText(this.player.injury_status.status_id)
    },
    injuryReport() {
      if (!this.isInjured) {
        return null
      }

      return this.statusText
    },
    injuryDetails() {
      return this.isInjured
        ? `${playerStatus.getFullText(this.injuryStatus.status_id)} - ${this.injuryStatus.injury}`
        : null
    },

    enablePlayerLinks() {
      return this.$root.enablePlayerLinks
    },
    shortName() {
      return `${this.player.first_name[0]}. ${this.player.last_name}`
    },
    displayName() {
      let name = this.shortenName ? this.shortName : this.player.full_name

      if (this.maxNameLength && name.length > this.maxNameLength) {
        return `${name.substring(0, this.maxNameLength)}...`
      } else {
        return name
      }
    },
    injurySeverity() {
      return this.isInjured ? playerStatus.getSeverity(this.injuryStatus.status_id) : ""
    },
    injuryIconColor() {
      return this.getInjuryIconColor(this.injurySeverity)
    },
    injuryIcon() {
      return this.getInjuryIcon(this.injurySeverity)
    },
    injuryTextColor() {
      return this.getInjuryIconColor(this.injurySeverity) + "--text"
    },
  },
  methods: {
    getInjuryIconColor(severity) {
      switch (severity) {
        case 3:
          return "red"
        case 2:
          return "red"
        case 1:
          return "amber"
        default:
          return ""
      }
    },
    getInjuryIcon(severity) {
      switch (severity) {
        case 3:
          return "mdi-hospital-box-outline"
        case 2:
          return "mdi-help-box-outline"
        case 1:
          return "mdi-bandage"
        default:
          return ""
      }
    },
  },
}
</script>
