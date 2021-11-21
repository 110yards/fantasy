import { firestore } from "../modules/firebase"

export default {
  data() {
    return {
      opponents: {},
    }
  },

  methods: {
    getOpponent(teamAbbreviation) {
      return teamAbbreviation in this.opponents ? this.opponents[teamAbbreviation] : "BYE"
    },
  },
  created() {
    this.$bind("opponents", firestore.doc("public/opponents"))
  },
}
