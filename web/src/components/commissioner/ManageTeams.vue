<template>
  <v-row>
    <v-col cols="12">
      <div v-if="editRosterId">
        <app-text-field label="Roster name" v-model="editRosterName" />
        <app-primary-button @click="updateRosterName()">Change name</app-primary-button>
        <app-default-button class="ml-2" @click="editRosterId = null">Cancel</app-default-button>
      </div>

      <div v-if="banRoster">
        <p v-if="!banRoster.name_changes_banned">
          Prevent <strong>{{ banRoster.name }}</strong> from changing roster name?
        </p>
        <p v-else>
          Allow <strong>{{ banRoster.name }}</strong> to change roster name again?
        </p>
        <app-primary-button @click="flipNameChangesBan()">Yes</app-primary-button>
        <app-default-button class="ml-2" @click="banRoster = null">No, cancel</app-default-button>
      </div>

      <v-simple-table class="table" v-if="!editRosterId && !banRoster">
        <template v-slot:default>
          <tbody>
            <tr v-for="roster in rosters" :key="roster.id">
              <td>
                <span>{{ roster.name }}</span>
              </td>

              <td class="test-right text-no-wrap">
                <v-icon @click="beginEditRosterName(roster)" small>mdi-lead-pencil</v-icon>
                <v-icon class="pl-1" v-if="!roster.name_changes_banned" @click="banRoster = roster" small
                  >mdi-cancel</v-icon
                >
                <v-icon class="pl-1" v-if="roster.name_changes_banned" @click="banRoster = roster" small
                  >mdi-restore</v-icon
                >
              </td>

              <td class="text-right" v-if="canRemove(roster)">
                <app-primary-button @click="confirmRemoval(roster)"> Remove </app-primary-button>
              </td>
              <td v-else></td>
            </tr>
          </tbody>
        </template>
      </v-simple-table>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import Vue from "vue"
import { firestore } from "../../modules/firebase"
import * as leagueService from "../../api/110yards/league"
import AppPrimaryButton from "../buttons/AppPrimaryButton.vue"
import AppTextField from "../inputs/AppTextField.vue"
import AppDefaultButton from "../buttons/AppDefaultButton.vue"
import { setNameChangeBan, updateRosterName } from "../../api/110yards/roster"

export default Vue.extend({
  components: {
    AppPrimaryButton,
    AppTextField,
    AppDefaultButton,
  },
  name: "manage-teams",
  props: ["leagueId"],
  data() {
    return {
      league: {},
      rosters: [],
      editRosterId: null,
      editRosterName: null,
      banRoster: null,
    }
  },
  computed: {
    uid() {
      return this.$store.state.uid
    },
    currentUser() {
      return this.$store.state.currentUser
    },
  },
  methods: {
    canRemove(roster) {
      return this.league && this.league.draft_state == "not_started" && roster.id != this.uid
    },
    removeRoster(roster) {
      leagueService.removeRoster(this.currentUser, this.leagueId, roster.id)
    },
    async confirmRemoval(roster) {
      let remove = confirm("Remove " + roster.name + " from this league?")
      if (remove) await this.removeRoster(roster)
    },

    beginEditRosterName(roster) {
      this.editRosterId = roster.id
      this.editRosterName = roster.name
    },

    async updateRosterName() {
      let command = {
        league_id: this.league.id,
        roster_id: this.editRosterId,
        roster_name: this.editRosterName,
      }
      await updateRosterName(command)
      this.editRosterId = null
    },

    async flipNameChangesBan() {
      let command = {
        league_id: this.league.id,
        roster_id: this.banRoster.id,
        banned: !this.banRoster.name_changes_banned,
      }
      await setNameChangeBan(command)
      this.banRoster = null
    },

    bindLeague(leagueId) {
      this.$bind("league", firestore.doc(`league/${leagueId}`))
    },
  },
  watch: {
    leagueId: {
      immediate: true,
      async handler(leagueId) {
        if (leagueId == null) return

        try {
          await this.bindLeague(leagueId)
          await this.$bind("rosters", firestore.collection("league").doc(leagueId).collection("roster"))
        } catch (exception) {
          this.$eventBus.$emit("exception", exception)
        }
      },
    },
  },
})
</script>
