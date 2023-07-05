import { firestore } from "../modules/firebase"

export default {
  data() {
    return {
      scoreboard: null,
    }
  },

  methods: {
    getOpponent(teamAbbreviation) {
      let opponent = this.scoreboard && this.scoreboard.teams ? this.scoreboard.teams[teamAbbreviation].opponent : null
      return opponent ? opponent.toUpperCase() : "BYE"
    },
    isLocked(teamAbbreviation) {
      if (!teamAbbreviation) return false
      return this.scoreboard && this.scoreboard.teams && this.scoreboard.teams[teamAbbreviation].locked
    },
    getGameForTeam(teamAbbreviation) {
      let team = this.scoreboard && this.scoreboard.teams ? this.scoreboard.teams[teamAbbreviation] : null
      return team != null ? team.game : null
    },
    getGameIdForTeam(teamAbbreviation) {
      let game = this.getGameForTeam(teamAbbreviation)
      return game ? game.game_id : null
    },
  },
  created() {
    this.$bind("scoreboard", firestore.doc("public/scoreboard"))
  },
}
