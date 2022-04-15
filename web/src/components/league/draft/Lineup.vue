<template>
  <v-simple-table>
    <template v-slot:default>
      <thead>
        <tr>
          <th>Pos</th>
          <th>Player</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="position in draftablePositions" :key="position.id">
          <td>{{ position.name }}</td>
          <td v-if="position.player">
            <player-link
              :player="position.player"
              :showShortPlayerStatus="true"
              :showStatus="false"
              :showNational="true"
              :leagueId="leagueId"
            />
          </td>
          <td v-else></td>
        </tr>
      </tbody>
    </template>
  </v-simple-table>
</template>

<style scoped></style>

<script>
import { selectablePositions } from "../../../api/110yards/constants"
import NationalStatus from "../../player/NationalStatus.vue"
import { playerStatus } from "../../../api/110yards/constants"
import PlayerLink from "../../player/PlayerLink.vue"

export default {
  components: { NationalStatus, PlayerLink },
  name: "lineup",
  props: {
    leagueId: {
      required: true,
      type: String,
    },
    roster: {
      required: true,
      type: Object,
    },
  },

  computed: {
    draftablePositions() {
      if (this.roster == null || this.roster.positions == null) return []

      let positions = Object.values(this.roster.positions)
      return positions.filter(p => selectablePositions.includes(p.position_type))
    },
  },

  methods: {
    isInjured(player) {
      return player.status_current != playerStatus.Active
    },
  },
}
</script>
