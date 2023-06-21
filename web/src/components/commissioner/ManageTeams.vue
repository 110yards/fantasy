<template>
  <v-row>
    <v-col cols="12">
      <div v-if="editRosterId">
        <app-text-field label="Roster name" v-model="editRosterName" />
        <app-primary-button @click="updateRosterName()">Change name</app-primary-button>
        <app-default-button class="ml-2" @click="editRosterId = null">Cancel</app-default-button>
      </div>

      <div v-if="editBudgetRoster">
        <p>
          Edit waiver budget for <strong>{{ editBudgetRoster.name }}</strong>
        </p>
        <app-number-field min="0" label="Waiver budget" v-model="editBudgetAmount" />
        <app-primary-button @click="updateRosterBudget()">Update budget</app-primary-button>
        <app-default-button class="ml-2" @click="editBudgetRoster = null">Cancel</app-default-button>
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

      <v-simple-table class="table" v-if="showTable">
        <template v-slot:default>
          <thead>
            <tr>
              <th>Name</th>
              <th>Waiver budget</th>
              <th></th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="roster in rosters" :key="roster.id">
              <td>
                <span>{{ roster.name }}</span>
              </td>
              <td>${{ roster.waiver_budget }}</td>

              <td class="test-right text-no-wrap">
                <v-menu offset-y>
                  <template v-slot:activator="{ on }">
                    <v-btn icon v-on="on">
                      <v-icon>mdi-dots-vertical</v-icon>
                    </v-btn>
                  </template>

                  <v-list>
                    <v-list-item @click="beginEditRosterName(roster)">
                      <v-list-item-title>Change name</v-list-item-title>
                    </v-list-item>

                    <v-list-item @click="banRoster = roster">
                      <v-list-item-title>
                        <span v-if="!roster.name_changes_banned">Block name changes</span>
                        <span v-else>Allow name changes</span>
                      </v-list-item-title>
                    </v-list-item>

                    <v-list-item @click="beginEditBudget(roster)">
                      <v-list-item-title>Adjust budget</v-list-item-title>
                    </v-list-item>

                    <v-list-item v-if="canRemove(roster)">
                      <v-list-item-title>
                        <app-primary-button @click="confirmRemoval(roster)"> Remove from league </app-primary-button>
                      </v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </td>
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
import AppNumberField from "../inputs/AppNumberField.vue"
import AppDefaultButton from "../buttons/AppDefaultButton.vue"
import { setNameChangeBan, updateRosterName, setWaiverBudget } from "../../api/110yards/roster"

export default Vue.extend({
  components: {
    AppPrimaryButton,
    AppTextField,
    AppDefaultButton,
    AppNumberField,
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
      editBudgetRoster: null,
      editBudgetAmount: null,
    }
  },
  computed: {
    uid() {
      return this.$store.state.uid
    },
    currentUser() {
      return this.$store.state.currentUser
    },
    showTable() {
      return !this.editRosterId && !this.banRoster && !this.editBudgetRoster
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

    beginEditBudget(roster) {
      this.editBudgetRoster = roster
      this.editBudgetAmount = roster.waiver_budget
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

    async updateRosterBudget() {
      let command = {
        league_id: this.league.id,
        roster_id: this.editBudgetRoster.id,
        waiver_budget: this.editBudgetAmount,
      }

      await setWaiverBudget(command)
      this.editBudgetRoster = null
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
