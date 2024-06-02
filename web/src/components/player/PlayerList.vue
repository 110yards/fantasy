<template>
  <div v-if="!showTable">
    <v-col v-if="playerToAdd" cols="12">
      <add-player
        :waiversActive="waiversActive"
        :player="playerToAdd"
        :currentRoster="currentRoster"
        :leagueId="leagueId"
        :players="players"
        v-on:cancel="playerToAdd = null"
      />
    </v-col>

    <v-card v-else class="player-list">
      <v-card-title>
        Players
        <v-btn v-if="!isDraft" icon title="Export players" @click="showTable = true"><v-icon>mdi-table</v-icon></v-btn>
      </v-card-title>
      <v-card-subtitle v-if="showPreviousSeasonStats">Past season stats</v-card-subtitle>
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
          <v-col cols="4" sm="1" class="mx-sm-2">
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

        <a href="https://github.com/mdryden/110yards/wiki#waivers" target="_blank">How do waivers work?</a>
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
            <player-link :player="item" :leagueId="leagueId" :showStatus="true" />
          </template>

          <template v-slot:[`item.opponent`]="{ item }">
            <span>{{ getNextOpponent(item) }}</span>
          </template>

          <template v-slot:[`item.points`]="{ item }">
            <score :score="item.points" />
          </template>

          <template v-slot:[`item.average`]="{ item }">
            <score :score="item.average" />
          </template>

          <template v-slot:[`item.last_week_score`]="{ item }">
            <score :score="item.last_week_score" />
          </template>

          <template v-slot:[`item.position`]="{ item }">
            {{ item.position.toUpperCase() }}
          </template>

          <template v-slot:[`item.owner`]="{ item }">
            <league-roster-link v-if="isOwned(item)" :leagueId="leagueId" :roster="getOwner(item.id)" :trim="true" />
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>

  <div v-else>
    <data-table :data="players" v-on:close="showTable = false" />
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
import { firestore, rtdb } from "../../modules/firebase"
import LeagueRosterLink from "../league/LeagueRosterLink.vue"
import { draftState, visiblePlayerPositions } from "../../api/110yards/constants"
import * as headers from "./positionHeaders"
import AppPrimaryButton from "../buttons/AppPrimaryButton.vue"
import AppDefaultButton from "../buttons/AppDefaultButton.vue"
import Locked from "../icons/Locked.vue"
import { longDate } from "../../modules/formatter"
import AddPlayer from "./AddPlayer.vue"
import { formatScore } from "../../modules/formatter"
import Score from "../Score.vue"
import { getCurrentPlayers, getDraftPlayers, getPlayersRef } from "../../api/110yards/league"
import DataTable from "./DataTable.vue"

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
    DataTable,
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
      playerToAdd: null,
      showTable: false,
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

    filteredPlayers() {
      let players = this.players

      if (this.freeAgentsOnly) {
        players = players.filter(p => !this.isOwned(p))
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

      if (!this.isDraft) {
        headers.push({
          text: "LW",
          value: "last_week_score",
        })
      }

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

    currentLeague() {
      return this.$root.currentLeague
    },

    showPreviousSeasonStats() {
      return this.isDraft || (this.currentLeague && this.currentLeague.draft_state != draftState.Complete)
    },
  },
  methods: {
    isOwned(player) {
      return player.id in this.playerOwners
    },

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

      return this.$root.isLocked(player.team.abbr)
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
      return player != null && player.team != null ? this.$root.getOpponent(player.team.abbr) : ""
    },

    getPlayerScore(player) {
      let filterResults = this.playerScores.filter(p => p.id == player.id)

      return filterResults && filterResults.length == 1 ? filterResults[0] : null
    },

    getPlayerStats(player) {
      let filterResults = this.seasonStats.filter(p => p.player_id == player.id)

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

    async getPlayersRef() {
      if (!this.leagueId || !this.uid) return

      let path = await getPlayersRef(this.leagueId) // todo change name
      let ref = rtdb.ref(path)

      this.$rtdbBind("players", ref)
    },

    configureReferences() {
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
    },
  },
  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        if (leagueId) {
          this.getPlayersRef()
          this.configureReferences()
        }
      },
    },

    uid: {
      immediate: true,
      handler(uid) {
        if (uid) {
          this.getPlayersRef()
        }
      },
    },
  },
}
</script>
