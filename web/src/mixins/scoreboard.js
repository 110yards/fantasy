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
      return this.scoreboard && this.scoreboard.teams && this.scoreboard.teams[teamAbbreviation].locked
    },
  },
  created() {
    this.$bind("scoreboard", firestore.doc("public/scoreboard"))
  },
}
