<template>
  <div>
    <v-btn @click="$emit('close')" class="mb-2">Close</v-btn>
    <pre id="dataTable">
{{ headers }}
<template v-for="player in data"><template v-for="key in keys">{{getValue(player, key)}},</template><br :key="player.id" /></template>
  </pre>
  </div>
</template>

<style scoped>
pre {
  overflow-x: scroll;
}
</style>

<script>
import { playerStatus } from "../../api/110yards/constants"
import * as headers from "./positionHeaders"

export default {
  props: {
    data: { type: Array, required: true },
  },

  computed: {
    headers() {
      const common = "First Name,Last Name,Team,Position,Status,Rank,Average,Points,Games Played,"
      return common
        .concat(headers.passing.map(x => x.text))
        .concat(",")
        .concat(headers.rushing.map(x => x.text))
        .concat(",")
        .concat(headers.receiving.map(x => x.text))
        .concat(",")
        .concat(headers.convert2.map(x => x.text))
        .concat(",")
        .concat(headers.kicking.map(x => x.text))
        .concat(",")
        .concat(headers.defense.map(x => x.text))
        .concat(",")
        .concat(headers.returns.map(x => x.text))
    },
    keys() {
      const common = [
        "first_name",
        "last_name",
        "team",
        "position",
        "status_current",
        "rank",
        "average",
        "points",
        "games_played",
      ]
      return common
        .concat(headers.passing.map(x => x.value))
        .concat(headers.rushing.map(x => x.value))
        .concat(headers.receiving.map(x => x.value))
        .concat(headers.convert2.map(x => x.value))
        .concat(headers.kicking.map(x => x.value))
        .concat(headers.defense.map(x => x.value))
        .concat(headers.returns.map(x => x.value))
    },
    stats() {},
  },

  methods: {
    getValue(player, key) {
      let isStat = false
      let statKey = ""
      if (key.includes("season_stats")) {
        isStat = !!player.season_stats
        statKey = key.replace("season_stats.", "")
      }

      switch (key) {
        case "first_name":
          return player.first_name.replace(",", "")
        case "last_name":
          return player.last_name.replace(",", "")
        case "team":
          return player.team.abbreviation
        case "position":
          return player.position.toUpperCase()
        case "status_current":
          return playerStatus.getFullText(player.status_current)
        default:
          return isStat ? player.season_stats[statKey] : player[key]
      }
    },
  },
}
</script>
