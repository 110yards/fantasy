<template>
  <div>
    <v-col v-if="playerToAdd" cols="12">
      <add-player
        :waiversActive="waiversActive"
        :player="playerToAdd"
        :currentRoster="currentRoster"
        :leagueId="leagueId"
        :playerScores="playerScores"
        v-on:cancel="playerToAdd = null"
      />
    </v-col>

    <v-card v-else class="player-list">
      <v-card-title>Players</v-card-title>
      <v-card-actions>
        <v-row>
          <v-col cols="4" sm="1" class="mx-sm-2" v-for="(position, index) in positions" :key="index">
            <v-btn
              v-on:click="togglePositionFilter(position.id)"
              class="position-toggle"
              :class="{
                'position-filter-active': filterActive(position.id),
              }"
              :data-position="position"
              :title="position.display"
            >
              {{ position.short }}
            </v-btn>
          </v-col>
          <v-col v-if="!isDraft" cols="4" sm="1" class="mx-sm-2">
            <v-btn
              type="button"
              class="position-toggle"
              :class="{
                'position-filter-active': freeAgentsOnly,
              }"
              @click="freeAgentsOnly = !freeAgentsOnly"
            >
              FA
            </v-btn>
          </v-col>
        </v-row>
      </v-card-actions>
      <v-card-actions>
        <app-text-field v-model="search" label="Search" class="mx-4" />
      </v-card-actions>

      <v-card-subtitle v-if="waiversActive">
        <v-alert dense color="warning">Waivers active until {{ waiversEnd }}</v-alert>

        <router-link :to="{ name: 'faq', hash: '#waivers' }">How do waivers work?</router-link>
      </v-card-subtitle>

      <v-card-text>
        <v-data-table
          mobile-breakpoint="0"
          v-if="players"
          :items="filteredPlayers"
          :headers="headers"
          sort-by="points"
          :sort-desc="true"
        >
          <template v-slot:top> </template>
          <template v-slot:[`item.actions`]="{ item }">
            <div v-if="showActions">
              <v-icon v-if="isAvailable(item) && !isLocked(item)" @click="addPlayer(item)">mdi-plus</v-icon>
              <locked v-if="isAvailable(item) && isLocked(item)" />

              <!-- auction draft -->
              <v-btn
                v-if="isAuction && isAvailable(item)"
                @click="nominateFunction(item)"
                icon
                title="Nominate this player"
              >
                <v-icon>mdi-export-variant</v-icon>
              </v-btn>
              <!-- /auction draft -->
            </div>
          </template>

          <template v-slot:[`item.display_name`]="{ item }">
            <player-link :player="item" :leagueId="leagueId" />
          </template>

          <template v-slot:[`item.points`]="{ item }">
            <!-- {{ formatScore(item.points) }} -->
            <score :score="item.points" />
          </template>

          <template v-slot:[`item.average`]="{ item }">
            <score :score="item.points" />
          </template>

          <template v-slot:[`item.position`]="{ item }">
            {{ item.position.toUpperCase() }}
          </template>

          <template v-slot:[`item.owner`]="{ item }">
            <league-roster-link v-if="item.owner" :leagueId="leagueId" :roster="item.owner" :trim="true" />
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<style scoped>
.position-toggle {
  margin-left: 1em;
}

.v-btn.position-filter-active {
  background-color: var(--v-primary_button-base);
}

.player-list >>> th[role="columnheader"],
.player-list >>> td {
  white-space: nowrap;
}
</style>

<script>
import AppCheckBox from "../../components/inputs/AppCheckBox.vue"
import AppTextField from "../../components/inputs/AppTextField.vue"
import PlayerLink from "../../components/player/PlayerLink.vue"
import { firestore } from "../../modules/firebase"
import LeagueRosterLink from "../league/LeagueRosterLink.vue"
import { visiblePlayerPositions } from "../../api/110yards/constants"
import * as headers from "./positionHeaders"
import AppPrimaryButton from "../buttons/AppPrimaryButton.vue"
import AppDefaultButton from "../buttons/AppDefaultButton.vue"
import Locked from "../icons/Locked.vue"
import { longDate } from "../../modules/formatter"
import AddPlayer from "./AddPlayer.vue"
import { formatScore } from "../../modules/formatter"
import Score from '../Score.vue'

export default {
  name: "player-list",
  components: {
    PlayerLink,
    AppTextField,
    AppCheckBox,
    LeagueRosterLink,
    AppPrimaryButton,
    AppDefaultButton,
    Locked,
    AddPlayer,
    Score,
  },
  props: {
    leagueId: null,
    showActions: {
      required: true,
      type: Boolean,
    },
    isDraft: {
      required: false,
      type: Boolean,
      default: false,
    },
    isAuction: {
      required: false,
      type: Boolean,
      default: false,
    },
    nominateFunction: {
      required: false,
      type: Function,
      default: () => {},
    },
    addFunction: {
      required: false,
      type: Function,
      default: null,
    },
    inputFilters: {
      required: false,
      type: Array,
      default() {
        return []
      },
    },
    toPositionId: {
      type: Number,
      required: false,
    },
  },
  data() {
    return {
      search: "",
      filterPositions: this.inputFilters,
      freeAgentsOnly: false,
      players: [],
      positions: [],
      ownedPlayers: [],
      rosters: null,
      playerScores: [],
      playerToAdd: null,
    }
  },
  computed: {
    uid() {
      return this.$store.state.uid
    },

    waiversActive() {
      return this.$root.state.waivers_active == true
    },

    waiversEnd() {
      return this.waiversActive ? longDate(this.$root.state.waivers_end.toDate()) : null
    },

    playerData() {
      let players = []

      // TODO: sort by rank?
      for (let player of this.players) {
        let playerScore = this.getPlayerScore(player)

        player.owner = this.getOwner(player.id)
        player.opponent = this.getNextOpponent(player)

        player.score = playerScore
        player.rank = playerScore != null ? playerScore.rank : ""
        player.average = playerScore != null ? playerScore.average_score : 0
        player.points = playerScore != null ? playerScore.total_score : 0
        player.games_played = playerScore != null ? playerScore.games_played : 0

        players.push(player)
      }

      return players
    },

    filteredPlayers() {
      let players = this.playerData

      if (this.freeAgentsOnly) {
        players = players.filter(p => p.owner == null)
      }

      players = players.filter(player => visiblePlayerPositions.includes(player.position))

      if (this.search) {
        players = players.filter(player => player.display_name.toLowerCase().indexOf(this.search.toLowerCase()) > -1)
      }

      if (this.filterPositions.length > 0) {
        players = players.filter(player => this.filterPositions.includes(player.position))
      }

      return players
    },
    headers() {
      let headers = [
        {
          text: "",
          value: "actions",
          sortable: false,
        },
        {
          text: "Player",
          value: "display_name",
        },
        {
          text: "Opp",
          value: "opponent",
        },
        {
          text: "Pos",
          value: "position",
        },
        {
          text: "Owner",
          value: "owner",
        },
        {
          text: "GP",
          value: "games_played",
        },
        {
          text: "Rk",
          value: "rank",
        },
        {
          text: "Points",
          value: "points",
        },
        {
          text: "Avg",
          value: "average",
        },
      ]

      headers = headers.concat(this.getPassingHeaders())
      headers = headers.concat(this.getRushingHeaders())
      headers = headers.concat(this.getReceivingHeaders())
      headers = headers.concat(this.getConvertTwoHeaders())
      headers = headers.concat(this.getKickingHeaders())
      headers = headers.concat(this.getReturnHeaders())
      headers = headers.concat(this.getDefenseHeaders())

      return headers
    },

    playerOwners() {
      return this.ownedPlayers.reduce((players, player) => ((players[player.id] = player), players), {})
    },

    currentRoster() {
      return this.rosters != null && this.uid ? this.rosters.filter(r => r.id == this.uid)[0] : null
    },
  },
  methods: {
    addPlayer(player) {
      // draft
      if (this.addFunction) {
        this.addFunction(player)
      } else {
        this.playerToAdd = player
      }
    },

    isLocked(player) {
      if (this.isDraft) return false

      return this.$root.isLocked(player.team.abbreviation)
    },

    searchPlayers(value, search, item) {
      return value != null && search != null && typeof value == "string" && value.toString().indexOf(search) !== -1
    },

    togglePositionFilter(position) {
      if (this.filterPositions.includes(position)) {
        this.filterPositions = this.filterPositions.filter(pos => pos != position)
      } else {
        this.filterPositions.push(position)
      }
    },

    filterActive(position) {
      return this.filterPositions.includes(position)
    },

    isAvailable(player) {
      return this.getOwnerId(player.id) == null
    },

    formatScore(score) {
      return formatScore(score)
    },

    getNextOpponent(player) {
      return player != null && player.team != null ? this.$root.getOpponent(player.team.abbreviation) : ""
    },

    getPlayerScore(player) {
      let filterResults = this.playerScores.filter(p => p.id == player.id)

      return filterResults && filterResults.length == 1 ? filterResults[0] : null
    },

    getOwnerId(playerId) {
      return playerId in this.playerOwners ? this.playerOwners[playerId].owner_id : null
    },

    getOwner(playerId) {
      let ownerId = this.getOwnerId(playerId)
      let filterResults = !!ownerId ? this.rosters.filter(r => r.id == ownerId) : null

      return filterResults && filterResults.length == 1 ? filterResults[0] : null
    },

    getPassingHeaders() {
      let shouldInclude = this.filterPositions.includes("qb")
      return !shouldInclude ? [] : headers.passing
    },

    getRushingHeaders() {
      let shouldInclude =
        this.filterPositions.includes("qb") ||
        this.filterPositions.includes("rb") ||
        this.filterPositions.includes("wr")

      return !shouldInclude ? [] : headers.rushing
    },

    getReceivingHeaders() {
      let shouldInclude = this.filterPositions.includes("rb") || this.filterPositions.includes("wr")

      return !shouldInclude ? [] : headers.receiving
    },

    getConvertTwoHeaders() {
      let shouldInclude =
        this.filterPositions.includes("qb") ||
        this.filterPositions.includes("rb") ||
        this.filterPositions.includes("wr")

      return !shouldInclude ? [] : headers.convert2
    },

    getKickingHeaders() {
      let shouldInclude = this.filterPositions.includes("k")

      return !shouldInclude ? [] : headers.kicking
    },

    getReturnHeaders() {
      let shouldInclude =
        this.filterPositions.includes("db") ||
        this.filterPositions.includes("rb") ||
        this.filterPositions.includes("wr")

      return !shouldInclude ? [] : headers.returns
    },

    getDefenseHeaders() {
      let shouldInclude =
        this.filterPositions.includes("db") ||
        this.filterPositions.includes("lb") ||
        this.filterPositions.includes("dl")

      return !shouldInclude ? [] : headers.defense
    },

    configureReferences() {
      let path = `season/${this.$root.currentSeason}/player`
      let playersRef = firestore.collection(path)
      this.$bind("players", playersRef)

      let positionsRef = firestore
        .collection("roster-positions")
        .where("is_player_position", "==", true)
        .orderBy("order")
      this.$bind("positions", positionsRef)

      let ownersPath = `league/${this.leagueId}/owned_player`
      let ownersRef = firestore.collection(ownersPath)
      this.$bind("ownedPlayers", ownersRef)

      let rostersPath = `league/${this.leagueId}/roster`
      let rostersRef = firestore.collection(rostersPath)
      this.$bind("rosters", rostersRef)

      let scoresPath = `league/${this.leagueId}/player_score`
      let scoresRef = firestore.collection(scoresPath)
      this.$bind("playerScores", scoresRef)
    },

    combineData() {},
  },
  watch: {
    leagueId: {
      immediate: true,
      handler(_) {
        this.configureReferences()
      },
    },
  },
}
</script>
