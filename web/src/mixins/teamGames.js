import { firestore } from "../modules/firebase"

export default {
  data() {
    return {
      teamGameIds: null,
    }
  },

  methods: {
    getGameForTeamId(teamAbbreviation) {
      if (!this.teamGameIds || !this.teamGameIds.games) {
        return null
      }

      return this.teamGameIds[teamAbbreviation]
    },

    getGameForTeam(teamAbbreviation, scoreboard) {
      if (!scoreboard || !scoreboard.games) {
        return null
      }

      for (let game of Object.values(scoreboard.games)) {
        if (game.away && game.away.abbr == teamAbbreviation) {
          return game
        }

        if (game.home && game.home.abbr == teamAbbreviation) {
          return game
        }
      }

      return null
    },
  },
  created() {
    this.$bind("teamGameIds", firestore.doc("public/team_games"))
  },
}
