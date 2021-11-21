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
        if (game.teams.away && game.teams.away.abbreviation == teamAbbreviation) {
          return game
        }

        if (game.teams.home && game.teams.home.abbreviation == teamAbbreviation) {
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
