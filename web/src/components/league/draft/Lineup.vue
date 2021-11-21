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
            <span>{{ position.player.first_name }} {{ position.player.last_name }}</span>
            <national-status v-if="position.player" :national_status="position.player.national_status" />
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

export default {
  components: { NationalStatus },
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
}
</script>
