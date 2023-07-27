<template>
  <v-card v-if="!reviewPlayer">
    <v-card-title>Approve new players</v-card-title>
    <v-card-subtitle>
      Players in the system are identified by name and date of birth. When new players are detected by the import
      system, there is a risk that it is because a player's name has changed, and they are not actually new to the
      system. To avoid issues with duplicate players, all new players must be approved manually.
    </v-card-subtitle>

    <v-card-text>
      <v-simple-table>
        <template>
          <thead>
            <tr>
              <th>Name</th>
              <th>Team</th>
              <th>Position</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody v-if="playersToApprove && playersToApprove.length != 0">
            <tr v-for="player in playersToApprove" :key="player.id">
              <td>{{ player.full_name }}</td>
              <td>
                <span class="team-icon" :class="player.team_abbr">{{ player.team_abbr.toUpperCase() }}</span>
              </td>
              <td>{{ player.position.toUpperCase() }}</td>
              <td>
                <AppPrimaryButton @click="review(player)">Review</AppPrimaryButton>
              </td>
            </tr>
          </tbody>

          <tbody v-else>
            <tr>
              <td colspan="4">No players to approve</td>
            </tr>
          </tbody>
        </template>
      </v-simple-table>
    </v-card-text>
  </v-card>

  <v-card v-else>
    <v-card-title>Review player</v-card-title>
    <v-card-subtitle>
      Please review the player below. If this player is already in the system, please select an existing player to match
      with.
    </v-card-subtitle>

    <v-card-text>
      {{ reviewPlayer.full_name }} - {{ reviewPlayer.team_abbr.toUpperCase() }} <br />
      <label>Position: </label>{{ reviewPlayer.position.toUpperCase() }}
    </v-card-text>

    <v-card-text v-if="matchPlayer">
      <v-alert color="orange" icon="mdi-alert">
        <strong>Warning:</strong> Matching this player with an existing player will link the two players together. This
        will cause issues with player stats if the two players are not actually the same person. Please be sure that
        this is the same player before matching.
      </v-alert>

      <div class="mb-5">
        <h3>Original player</h3>
        <label>Name:</label> {{ matchPlayer.full_name }} <br />
        <label>Date of birth: </label>{{ formatDate(matchPlayer.birth_date.toDate()) }}
      </div>
      <div class="mb-5">
        <h3>Updated player</h3>
        <label>Name:</label> {{ reviewPlayer.full_name }} <br />
        <label>Date of birth: </label>{{ formatDate(reviewPlayer.birth_date.toDate()) }}
      </div>

      <AppPrimaryButton @click="match()">Confirm and match players</AppPrimaryButton>
      <AppDefaultButton @click="matchPlayer = null" class="ml-2">Cancel</AppDefaultButton>
    </v-card-text>

    <v-card-text v-else>
      <h3>Search for matches: <AppTextField v-model="searchCriteria" /></h3>
      <h5>Note: if a player's name has changed, he may appear as a free agent in the matches list.</h5>
      <v-simple-table>
        <template>
          <thead>
            <tr>
              <th>Name</th>
              <th>Team</th>
              <th>Position</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody v-if="anyMatches">
            <tr v-for="player in matches" :key="player.id">
              <td>{{ player.full_name }}</td>
              <td>
                <span v-if="!player.is_free_agent" class="team-icon" :class="player.team_abbr">{{
                  player.team_abbr.toUpperCase()
                }}</span>
                <span v-else>Free agent</span>
              </td>
              <td>{{ player.position.toUpperCase() }}</td>
              <td>
                <AppPrimaryButton @click="matchPlayer = player">Match</AppPrimaryButton>
              </td>
            </tr>
          </tbody>
          <tbody v-else>
            <tr>
              <td v-if="criteriaTooShort" colspan="4">Enter a search criteria to find matches</td>
              <td v-else colspan="4">No matches for "{{ searchCriteria }}"</td>
            </tr>
          </tbody>
        </template>
      </v-simple-table>
    </v-card-text>

    <v-card-actions v-if="!matchPlayer">
      <AppPrimaryButton @click="addNew()">Add new player</AppPrimaryButton>
      <AppDefaultButton @click="clear()">Cancel</AppDefaultButton>
    </v-card-actions>
  </v-card>
</template>

<script>
import { firestore } from "../../modules/firebase/index.js"
import AppDefaultButton from "../buttons/AppDefaultButton.vue"
import AppPrimaryButton from "../buttons/AppPrimaryButton.vue"
import AppTextField from "../inputs/AppTextField.vue"
import { addNewPlayer, matchPlayer } from "../../api/110yards/mod.js"
import { birthDate } from "../../modules/formatter/index.js"

export default {
  name: "Players",
  components: { AppPrimaryButton, AppDefaultButton, AppTextField },
  data() {
    return {
      playersToApprove: null,
      reviewPlayer: null,
      players: null,
      searchCriteria: null,
      matchPlayer: null,
    }
  },
  methods: {
    formatDate(date) {
      return birthDate(date)
    },

    review(player) {
      this.reviewPlayer = player
      this.searchCriteria = player.last_name
    },

    async addNew() {
      let command = {
        approval_player_id: this.reviewPlayer.player_id,
      }

      await addNewPlayer(command)
      this.clear()
    },

    async match() {
      let command = {
        approval_player_id: this.reviewPlayer.player_id,
        match_player_id: this.matchPlayer.player_id,
      }

      await matchPlayer(command)
      this.clear()
    },

    clear() {
      this.reviewPlayer = null
      this.matchPlayer = null
    },
  },
  computed: {
    anyMatches() {
      return this.matches.length > 0
    },

    criteriaTooShort() {
      return this.searchCriteria == null || this.searchCriteria.length < 2
    },

    matches() {
      if (this.criteriaTooShort) {
        return []
      }

      let matches = []
      for (let player of this.players) {
        if (!player.full_name) {
          console.log("No full name for player", player)
          continue
        }
        let matchA = player.full_name.toLowerCase().includes(this.searchCriteria.toLowerCase())
        let matchB = this.searchCriteria.toLowerCase().includes(player.last_name.toLowerCase())

        if (matchA || matchB) {
          matches.push(player)
        }
      }

      return matches
    },
  },
  mounted() {
    let approvals = firestore.collection("mod/approvals/players")
    this.$bind("playersToApprove", approvals)

    let playersRef = firestore.collection("players")
    this.$bind("players", playersRef)
  },
}
</script>
