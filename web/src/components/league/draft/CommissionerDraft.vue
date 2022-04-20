<template>
  <div v-if="draft && rosters">
    <div v-if="draft && rosters" class="draft">
      <v-row v-if="isCommissioner">
        <v-col cols="12">
          <commissioner-draft-tools :draft="draft" :leagueId="leagueId" :previousSlot="previousSlot" />
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12">
          <v-alert type="info" v-if="!isCommissioner && draft.is_paused">The commissioner has paused the draft</v-alert>
          <draft-events :events="draft.draft_events" />
        </v-col>
      </v-row>

      <v-row>
        <!-- <v-col cols="12" md="6">
          <draft-picks-list :rosters="rosters" :slots="upcomingPicks" title="Upcoming Picks" />
        </v-col>

        <v-col cols="12" md="6">
          <draft-picks-list :rosters="rosters" :slots="completedPicks" title="Completed Picks" />
        </v-col> -->
      </v-row>
      <v-row>
        <v-col cols="12" md="9">
          <player-list
            :leagueId="leagueId"
            :showActions="isCommissioner && !draft.is_paused"
            :addFunction="addPlayer"
            :isDraft="true"
          />
        </v-col>
        <v-col cols="12" md="3">
          <draft-rosters
            :isAuction="false"
            :leagueId="leagueId"
            :rosters="rosters"
            :isCommissionerDraft="true"
            :isCommissioner="isCommissioner"
            v-on:rosterChange="updateSelectedRosterId"
          />
        </v-col>
      </v-row>
    </div>
  </div>
</template>

<script>
import { selectPlayer } from "../../../api/110yards/league"
import eventBus from "../../../modules/eventBus"
import PlayerList from "../../player/PlayerList.vue"
import CommissionerDraftTools from "./CommissionerDraftTools.vue"
import DraftEvents from "./DraftEvents.vue"
import DraftRosters from "./DraftRosters.vue"

export default {
  components: { DraftEvents, CommissionerDraftTools, PlayerList, DraftRosters },
  name: "commissioner-draft",
  props: {
    draft: {
      type: Object,
      required: true,
    },
    rosters: {
      type: Array,
      required: true,
    },
    leagueId: {
      type: String,
      required: true,
    },
    isCommissioner: {
      type: Boolean,
      required: true,
    },
  },

  data() {
    return {
      selectedRosterId: null,
    }
  },

  computed: {
    currentUser() {
      return this.$store.state.currentUser
    },

    currentSlot() {
      if (!this.draft || !this.rosters) return null

      let nextPick = this.draft.slots.find(s => s.completed == false)

      return nextPick
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
    updateSelectedRosterId(event) {
      this.selectedRosterId = event.rosterId
    },

    async addPlayer(player) {
      let command = {
        pick_number: this.currentSlot.pick_number,
        roster_id: this.selectedRosterId,
        league_id: this.leagueId,
        player_id: player.id,
      }

      let result = await selectPlayer(this.currentUser, this.leagueId, command)
    },
  },
}
</script>
