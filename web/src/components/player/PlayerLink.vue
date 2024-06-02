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

      <span v-if="showTeamName" class="pl-1">{{ player.team.abbr || player.team.abbreviation }}</span>
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

      <national-status v-if="showNational" :national_status="player.national_status" />
    </template>

    <!-- right to left -->
    <template v-else>
      <national-status v-if="showNational" :national_status="player.national_status" />

      <v-icon v-if="showShortPlayerStatus && isInjured" :color="injuryIconColor" small>{{ injuryIcon }}</v-icon>
      <span :class="injuryTextColor" v-if="showPlayerStatus && !showShortPlayerStatus" :title="injuryDetails">
        {{ injuryReport }}
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

      <span v-if="showTeamName" class="">{{ player.team.abbr }}</span>
      <span v-if="showPosition" class="">&nbsp;- {{ player.position.toUpperCase() }}</span>

      <span v-if="showTeamLogo" class="team-icon pl-1" :class="team"> </span>
    </template>
  </span>
</template>

<style scoped></style>

<script>
import { playerStatus } from "../../api/110yards/constants"
import NationalStatus from "./NationalStatus.vue"

export default {
  name: "player-link",
  components: {
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
      return this.player.team != null ? this.player.team.abbr || this.player.team.abbreviation : "FA" // abbr || abbreviation is because I pushed a bad update early 2024. can go away eventually.
    },
    showPlayerStatus() {
      return this.isInjured
    },
    isInjured() {
      return this.player.injury_status != null
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
      let name = this.shortenName ? this.shortName : this.player.display_name

      if (this.maxNameLength && name.length > this.maxNameLength) {
        return `${name.substring(0, this.maxNameLength)}...`
      } else {
        return name
      }
    },
    injurySeverity() {
      return playerStatus.getSeverity(this.injuryStatus.status_id)
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
