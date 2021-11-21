<template>
  <div class="mt-5">
    <router-link :to="{ name: 'faq', hash: '#waivers' }">How do waivers work?</router-link>

    <h4>Active bids</h4>
    <v-simple-table>
      <template>
        <thead>
          <tr>
            <th></th>
            <th>Player</th>
            <th>Bid</th>
            <th>Drop Player</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!roster.waiver_bids || roster.waiver_bids.length == 0">
            <td colspan="4">You haven't bid on any yet this week</td>
          </tr>

          <tr v-for="(bid, index) in roster.waiver_bids" :key="index">
            <td>
              <app-default-button @click="cancelBid(index)">Cancel</app-default-button>
            </td>
            <td><player-link :leagueId="leagueId" :player="bid.player" /></td>
            <td>${{ bid.amount }}</td>
            <td>
              <player-link v-if="bid.drop_player" :leagueId="leagueId" :player="bid.drop_player" />
              <span v-else>N/A</span>
            </td>
          </tr>
        </tbody>
      </template>
    </v-simple-table>

    <h4 class="mt-5">Recent bids</h4>

    <v-simple-table>
      <template>
        <thead>
          <tr>
            <th>Player</th>
            <th>Bid</th>
            <th>Drop Player</th>
            <th>Result</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(bid, index) in roster.processed_waiver_bids" :key="index">
            <td><player-link :leagueId="leagueId" :player="bid.player" :showTeamLogo="false" /></td>
            <td>${{ bid.amount }}</td>
            <td>
              <player-link
                v-if="bid.drop_player"
                :leagueId="leagueId"
                :player="bid.drop_player"
                :showTeamLogo="false"
              />
              <span v-else>N/A</span>
            </td>
            <td>
              {{ getBidResult(bid.result) }}
            </td>
          </tr>

          <tr v-if="!roster.processed_waiver_bids || roster.processed_waiver_bids.length == 0">
            <td colspan="4">No recently processed bids</td>
          </tr>
        </tbody>
      </template>
    </v-simple-table>
  </div>
</template>

<script>
import AppDefaultButton from "../../../components/buttons/AppDefaultButton.vue"
import PlayerLink from "../../../components/player/PlayerLink.vue"
import { cancelBid } from "../../../api/110yards/roster"
import { waiverBidResult } from "../../../api/110yards/constants"

export default {
  components: { PlayerLink, AppDefaultButton },
  name: "Waivers",

  props: {
    roster: { type: Object, required: true },
    leagueId: { type: String, required: true },
  },

  methods: {
    getBidResult(result) {
      return waiverBidResult.getText(result)
    },

    async cancelBid(index) {
      let command = {
        league_id: this.leagueId,
        roster_id: this.roster.id,
        bid_index: index,
      }

      await cancelBid(command)
    },
  },
}
</script>
