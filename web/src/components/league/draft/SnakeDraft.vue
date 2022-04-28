<template>
  <div v-if="draft && rosters" class="draft">
    <v-row v-if="isCommissioner">
      <v-col cols="12">
        <commissioner-draft-tools :draft="draft" :leagueId="leagueId" :previousSlot="previousSlot" />
      </v-col>
    </v-row>

    <v-row v-if="draft.is_paused">
      <v-col cols="12">
        <v-alert type="info" v-if="!isCommissioner">The commissioner has paused the draft</v-alert>
        <draft-events :events="draft.draft_events" />
      </v-col>
    </v-row>

    <v-row v-if="!draft.is_paused && yourTurn">
      <v-col cols="12">
        <v-alert type="success">It's your turn, select a player from the list</v-alert>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="6">
        <draft-picks-list :rosters="rosters" :slots="upcomingPicks" title="Upcoming Picks" />
      </v-col>

      <v-col cols="12" md="6">
        <draft-picks-list :rosters="rosters" :slots="completedPicks" title="Completed Picks" />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" md="9">
        <player-list
          :leagueId="leagueId"
          :isDraft="true"
          :showActions="yourTurn && !draft.is_paused"
          :addFunction="addPlayer"
        >
        </player-list>
      </v-col>
      <v-col cols="12" md="3">
        <draft-rosters :isAuction="false" :leagueId="leagueId" :rosters="rosters" />
      </v-col>
    </v-row>

    <v-row v-if="!draft.is_paused">
      <v-col cols="12">
        <draft-events :events="draft.draft_events" />
      </v-col>
    </v-row>
  </div>
</template>

<script>
import Lineup from "../../../components/league/draft/Lineup"
import PlayerList from "../../../components/player/PlayerList.vue"
import DraftEvents from "../../../components/league/draft/DraftEvents.vue"
import SnakeSlot from "../../../components/league/draft/SnakeSlot.vue"
import CommissionerDraftTools from "../../../components/league/draft/CommissionerDraftTools.vue"
import DraftRosters from "./DraftRosters.vue"
import DraftPicksList from "./DraftPicksList.vue"
import { selectPlayer } from "../../../api/110yards/league"
import eventBus from "../../../modules/eventBus"

export default {
  name: "draft",
  components: {
    Lineup,
    PlayerList,
    DraftEvents,
    SnakeSlot,
    CommissionerDraftTools,
    DraftRosters,
    DraftPicksList,
  },
  props: {
    leagueId: {
      type: String,
      required: true,
    },
    draft: {
      type: Object,
      required: true,
    },
    rosters: {
      type: Array,
      required: true,
    },
    isCommissioner: {
      type: Boolean,
      required: true,
    },
  },
  computed: {
    yourTurn() {
      return this.currentSlot != null && this.currentSlot.roster_id == this.currentRosterId
    },

    completedPicks() {
      return this.draft.slots.filter(s => s.completed).reverse()
    },

    upcomingPicks() {
      return this.draft.slots.filter(s => !s.completed)
    },

    currentRosterId() {
      return this.$store.state.uid
    },

    currentUser() {
      return this.$store.state.currentUser
    },

    currentSlot() {
      if (!this.draft || !this.rosters) return null

      let nextPick = this.draft.slots.find(s => s.completed == false)

      return nextPick
    },

    pickNumber() {
      return this.currentSlot != null ? this.currentSlot.pick_number : null
    },

    previousSlot() {
      if (!this.draft || !this.rosters) return null

      let completedPicks = this.draft.slots.filter(s => s.completed == true)

      if (completedPicks.length > 0) {
        return completedPicks[completedPicks.length - 1]
      }

      return null
    },
  },
  methods: {
    async addPlayer(player) {
      let command = {
        pick_number: this.currentSlot.pick_number,
        roster_id: this.currentRosterId,
        league_id: this.leagueId,
        player_id: player.id,
      }

      let result = await selectPlayer(this.currentUser, this.leagueId, command)
    },
  },

  watch: {
    yourTurn: {
      immediate: true,
      handler(yourTurn) {
        if (yourTurn) {
          eventBus.$emit("show-success", "It's your turn")
        }
      },
    },
  },
}
</script>
