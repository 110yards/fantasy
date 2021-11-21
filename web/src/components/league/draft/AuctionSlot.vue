<template>
  <v-card v-if="draftSlot">
    <v-card-title>Auction Draft, Pick {{ draftSlot.pick_number }}</v-card-title>

    <v-card-text v-if="!biddingStarted">
      <div>Nominator: {{ getRosterName(draftSlot.nominator) }}</div>
      <div>Player: TBD</div>
    </v-card-text>

    <v-card-text v-if="biddingStarted">
      <div>
        Player: <player-link v-if="draftSlot.player" :leagueId="leagueId" :player="draftSlot.player" /> nominated by
        {{ getRosterName(draftSlot.nominator) }}
      </div>

      <div>Bid: ${{ draftSlot.bid ? draftSlot.bid : 0 }} - {{ getRosterName(draftSlot.roster_id) }}</div>
    </v-card-text>

    <v-card-text v-if="biddingStarted && !isPaused">
      <!--<div>Next to bid: {{ nextBidderName }}</div> -->
      <div v-for="bidder in draftSlot.bidders" :key="bidder.index">
        {{ getRosterName(bidder.roster_id) }} - {{ getBidderStatus(bidder) }}
      </div>
    </v-card-text>

    <v-card-text v-if="biddingStarted && isPaused && isCommissioner">
      TODO: Allow commissioner to force a winning bid for a user
    </v-card-text>

    <v-card-text v-if="tip && !isPaused" class="warning--text">
      <div class="tip">{{ tip }}</div>
    </v-card-text>

    <v-card-actions>
      <v-row v-if="yourTurn">
        <v-col cols="4">
          <v-text-field v-model.number="bid" type="number" outlined filled dense required :max="maxBid" :min="minBid" />
        </v-col>
        <v-col cols="2">
          <app-primary-button @click="placeBid()">Bid</app-primary-button>
        </v-col>
        <v-col>
          <app-default-button @click="passBid()">Pass</app-default-button>
        </v-col>
      </v-row>
    </v-card-actions>
  </v-card>
</template>

<style scoped>
.tip {
  font-weight: bold;
}
</style>

<script>
import { bidOnAuction, passBidOnAuction } from "../../../api/110yards/league"
import eventBus from "../../../modules/eventBus"
import AppDefaultButton from "../../buttons/AppDefaultButton.vue"
import AppPrimaryButton from "../../buttons/AppPrimaryButton.vue"
import AppNumberField from "../../inputs/AppNumberField.vue"
import PlayerLink from "../../player/PlayerLink.vue"

export default {
  props: {
    draftType: { type: String, required: true },
    draftSlot: { type: Object, required: false },
    isPaused: { type: Boolean, required: true },
    rosters: { type: Array, required: true },
    leagueId: { type: String, required: true },
    isCommissioner: { type: Boolean, required: false, default: false },
  },
  components: {
    PlayerLink,
    AppPrimaryButton,
    AppNumberField,
    AppDefaultButton,
  },

  data() {
    return {
      bid: 0,
    }
  },

  computed: {
    currentRosterId() {
      return this.$store.state.uid
    },

    currentUser() {
      return this.$store.state.currentUser
    },

    currentRoster() {
      return this.rosters.find(r => r.id == this.currentRosterId)
    },

    tip() {
      let needsToNominate = !this.biddingStarted && this.draftSlot.nominator === this.currentRosterId
      if (needsToNominate)
        return "It's your turn, nominate a player from the list. Nominated players must be able to fit on your roster."

      let needsToBid = this.biddingStarted && this.nextBidder && this.nextBidder.roster_id == this.currentRosterId
      if (needsToBid) return `It's your turn to bid or pass. You may bid up to $${this.maxBid}.`

      return ""
    },

    biddingStarted() {
      return !!this.draftSlot.player
    },

    nextBidderName() {
      return this.nextBidder ? this.getRosterName(this.nextBidder.roster_id) : ""
    },

    nextBidder() {
      return this.draftSlot.player ? this.draftSlot.bidders[this.draftSlot.bidder_index] : null
    },

    yourTurn() {
      return this.nextBidder && this.nextBidder.roster_id == this.currentRosterId
    },

    minBid() {
      return this.draftSlot.bid + 1
    },
    maxBid() {
      return this.currentRoster != null ? this.currentRoster.draft_budget : 0
    },
  },

  methods: {
    getRoster(rosterId) {
      return this.rosters.find(r => r.id == rosterId)
    },

    getRosterName(rosterId) {
      let roster = this.getRoster(rosterId)

      return roster != null ? roster.name : ""
    },

    getBidderStatus(bidder) {
      console.log(bidder)
      if (bidder.passed) return "Passed"
      if (bidder.outbid) return "Out Bid"
      if (bidder.in_eligible) return "Ineligible"
      if (bidder.index == this.draftSlot.bidder_index) return "On the clock"
      return "Waiting"
    },

    async placeBid() {
      if (this.bid === "") {
        eventBus.$emit("show-error", "You must enter a bid")
        return
      }

      if (this.bid < this.minBid) {
        eventBus.$emit("show-error", `Minimum bid is $${this.minBid}`)
        return
      }

      let command = {
        league_id: this.leagueId,
        pick_number: this.draftSlot.pick_number,
        bidder: this.currentRosterId,
        bid_amount: this.bid,
      }

      let result = await bidOnAuction(this.currentUser, this.leagueId, command)
    },

    async passBid() {
      let command = {
        league_id: this.leagueId,
        pick_number: this.draftSlot.pick_number,
        bidder: this.currentRosterId,
      }

      let result = await passBidOnAuction(this.currentUser, this.leagueId, command)
    },
  },

  watch: {
    yourTurn: {
      immediate: true,
      handler(yourTurn) {
        if (yourTurn) {
          this.bid = this.minBid
        }
      },
    },
  },
}
</script>
