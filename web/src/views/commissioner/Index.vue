<template>
  <div v-if="isCommissioner && league != null">
    <v-card>
      <v-card-title>Commmissioner Tools</v-card-title>
      <v-card-subtitle>
        <v-alert type="info" v-if="showDraftNotReadyTip">Generate a schedule to enable the draft</v-alert>
      </v-card-subtitle>

      <v-card-text>
        <v-btn class="caption" text @click="setView('registration')">Registration</v-btn>
        <v-btn class="caption" text @click="setView('league-options')">League options</v-btn>
        <v-btn class="caption" text @click="setView('scoring')">Scoring</v-btn>
        <v-btn class="caption" text @click="setView('manage-teams')">Manage Teams</v-btn>
        <v-btn class="caption" text v-if="hasDraftOrder && !leagueStarted" @click="setView('draft-order')">
          Draft Order
        </v-btn>
        <v-btn class="caption" text v-if="isAuction" @click="setView('budgets')">Draft Budgets</v-btn>
        <v-btn class="caption" text @click="setView('rosters')">Roster options</v-btn>
        <v-btn class="caption" text @click="setView('schedule')">Schedule settings</v-btn>
      </v-card-text>

      <v-card-text>
        <registration v-if="view == 'registration'" :league="league" :leagueStarted="leagueStarted" />
        <league-options v-if="view == 'league-options'" :league="league" :leagueStarted="leagueStarted" />
        <scoring-settings v-if="view == 'scoring'" :leagueId="leagueId" :leagueStarted="leagueStarted" />
        <manage-teams v-if="view == 'manage-teams'" :leagueId="leagueId" />
        <draft-order v-if="view == 'draft-order'" :league="league" :leagueStarted="leagueStarted" />
        <budgets v-if="view == 'budgets'" :league="league" :leagueStarted="leagueStarted" />
        <rosters v-if="view == 'rosters'" :leagueId="leagueId" :leagueStarted="leagueStarted" />
        <schedule v-if="view == 'schedule'" :leagueId="leagueId" :leagueStarted="leagueStarted" />
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { firestore } from "../../modules/firebase"
import LeagueOptions from "../../components/commissioner/LeagueOptions"
import ManageTeams from "../../components/commissioner/ManageTeams"
import Registration from "../../components/commissioner/Registration"
import Rosters from "../../components/commissioner/Rosters"
import Schedule from "../../components/commissioner/Schedule"
import DraftOrder from "../../components/commissioner/DraftOrder"
import { draftType, draftState } from "../../api/110yards/constants"
import Budgets from "../../components/commissioner/Budgets.vue"
import ScoringSettings from "../../components/commissioner/ScoringSettings.vue"

export default {
  name: "commissioner-index",
  components: {
    LeagueOptions,
    ManageTeams,
    Registration,
    Rosters,
    Schedule,
    DraftOrder,
    Budgets,
    ScoringSettings,
  },
  props: ["leagueId"],
  data() {
    return {
      league: null,
      view: "registration",
    }
  },
  computed: {
    isAdmin() {
      return this.$store.state.isAdmin
    },
    isCommissioner() {
      return this.league != null && (this.league.commissioner_id == this.$store.state.uid || this.isAdmin)
    },

    showDraftNotReadyTip() {
      return this.isCommissioner && !this.league.schedule_generated
    },

    canSetDraftOrder() {
      return this.league != null && this.league.draft_type == draftType.Snake
    },

    leagueStarted() {
      return this.league != null && this.league.draft_state != draftState.NotStarted
    },

    isAuction() {
      return this.league != null && this.league.draft_type == draftType.Auction
    },

    hasDraftOrder() {
      return this.league != null && this.league.draft_type != draftType.Commissioner
    },
  },

  methods: {
    setView(view) {
      this.view = view
    },
    leagueOptions() {
      this.view = "league-options"
    },
    manageTeams() {
      this.view = "manage-teams"
    },
    registration() {
      this.view = "registration"
    },
    rosters() {
      this.view = "rosters"
    },
  },

  watch: {
    leagueId: {
      immediate: true,
      async handler(leagueId) {
        console.log("league id watcher")
        if (leagueId == null) return

        try {
          await this.$bind("league", firestore.collection("league").doc(leagueId))
        } catch (exception) {
          this.$eventBus.$emit("exception", exception)
        }
      },
    },
  },
}
</script>

<style scoped>
.active-tool {
  padding-top: 1em;
  padding-bottom: 1em;
}
</style>
