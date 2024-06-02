<template>
  <v-data-table mobile-breakpoint="0" v-if="players" :items="players" :headers="headers" hide-default-footer="true">
    <template v-slot:top> </template>
    <template v-slot:[`item.actions`]="{ item }">
      <div v-if="showActions">
        <v-icon v-if="!isLocked(item)" @click="addPlayer(item)">mdi-plus</v-icon>
        <locked v-if="isLocked(item)" />
      </div>
    </template>

    <template v-slot:[`item.display_name`]="{ item }">
      <player-link :player="item" :leagueId="leagueId" />
    </template>

    <template v-slot:[`item.opponent`]="{ item }">
      {{ getNextOpponent(item) }}
    </template>

    <template v-slot:[`item.position`]="{ item }">
      {{ item.position.toUpperCase() }}
    </template>

    <template v-slot:[`item.points`]="{ item }">
      {{ getSeasonPoints(item) }}
    </template>
  </v-data-table>
</template>

<script>
import PlayerLink from "./PlayerLink.vue"
export default {
  components: { PlayerLink },
  name: "ComparePlayerTable",
  props: {
    showActions: { type: Boolean, required: true },
    players: { type: Array, required: true },
    playerScores: { type: Array, required: true },
    leagueId: { type: String, required: true },
  },

  computed: {
    headers() {
      let headers = [
        {
          text: "",
          value: "actions",
          sortable: false,
        },
        {
          text: "Player",
          value: "display_name",
        },
        {
          text: "Opp",
          value: "opponent",
        },
        {
          text: "Pos",
          value: "position",
        },
        {
          text: "GP",
          value: "games_played",
        },
        // {
        //   text: "Rk",
        //   value: "rank",
        // },
        {
          text: "Points",
          value: "points",
        },
        {
          text: "Avg",
          value: "average",
        },
      ]

      return headers
    },
  },

  methods: {
    getNextOpponent(player) {
      return player != null && player.team != null ? this.$root.getOpponent(player.team.abbr) : ""
    },

    getSeasonPoints(player) {
      let filterResults = this.playerScores.filter(p => p.id == player.id)

      let playerScore = filterResults && filterResults.length == 1 ? filterResults[0] : null

      return playerScore != null && playerScore.season_score != null ? playerScore.season_score.total_score : ""
    },

    isLocked(player) {
      return this.$root.isLocked(player.team.abbr)
    },
  },
}
</script>
