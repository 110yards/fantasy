import { firestore } from "../modules/firebase"

export default {
  data() {
    return {
      scoreboard: null,
    }
  },

  methods: {},
  created() {
    this.$bind("scoreboard", firestore.doc("public/scoreboard"))
  },
}
