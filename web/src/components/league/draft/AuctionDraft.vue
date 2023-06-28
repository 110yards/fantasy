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

    <v-row>
      <v-col cols="12" md="6">
        <auction-slot
          :draftType="draft.draft_type"
          :draftSlot="currentSlot"
          :rosters="rosters"
          :leagueId="leagueId"
          :isPaused="draft.is_paused"
          :isCommissioner="isCommissioner"
        />
      </v-col>
      <v-col cols="12" md="6"> <last-draft-pick-card :draft="draft" /> </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" md="9">
        <player-list
          :leagueId="leagueId"
          :showActions="showPlayerActions"
          :isAuction="true"
          :nominateFunction="nominatePlayer"
        >
        </player-list>
      </v-col>
      <v-col cols="12" md="3">
        <draft-rosters
          :isAuction="true"
          :leagueId="leagueId"
          :rosters="rosters"
          v-on:rosterChange="updateSelectedRoster"
        />
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
import PlayerList from "../../../components/player/PlayerList.vue"
import AuctionSlot from "../../../components/league/draft/AuctionSlot.vue"
import { nominateForAuction } from "../../../api/110yards/league"
import eventBus from "../../../modules/eventBus"
import DraftEvents from "../../../components/league/draft/DraftEvents.vue"
import CommissionerDraftTools from "../../../components/league/draft/CommissionerDraftTools.vue"
import LastDraftPickCard from "./LastDraftPickCard.vue"
import DraftRosters from "./DraftRosters.vue"

export default {
  name: "AuctionDraft",
  components: {
    PlayerList,
    AuctionSlot,
    DraftEvents,
    CommissionerDraftTools,
    LastDraftPickCard,
    DraftRosters,
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

  data() {
    return {
      selectedRoster: null,
    }
  },

  computed: {
    yourTurn() {
      if (!this.currentSlot.player) {
        return this.currentSlot.nominator == this.currentRosterId
      } else {
        return false // next bid in slot
      }
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

    previousSlot() {
      if (!this.draft || !this.rosters) return null

      let completedPicks = this.draft.slots.filter(s => s.completed == true)

      if (completedPicks.length > 0) {
        return completedPicks[completedPicks.length - 1]
      }

      return null
    },

    showPlayerActions() {
      if (!this.draft.is_paused) {
        return this.yourTurn
      } else {
        return this.isCommissioner
      }
    },
  },
  methods: {
    async nominatePlayer(player) {
      let command = {
        pick_number: this.currentSlot.pick_number,
        league_id: this.leagueId,
        player_id: player.player_id,
        nominator: this.currentRosterId,
      }

      if (this.draft.is_paused) {
        alert("confirm w/ roster target")
      } else {
        alert("confirm nominate player")
      }

      let result = await nominateForAuction(this.currentUser, this.leagueId, command)
    },

    updateSelectedRoster(event) {
      this.selectedRoster = event
    },
  },
}
</script>
