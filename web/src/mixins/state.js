import { firestore } from "../modules/firebase"

export default {
  data() {
    return {
      state: {},
    }
  },

  computed: {
    anyLocks() {
      return this.state.locks && Object.values(this.state.locks).filter(x => x == true).length > 0
    },
  },

  methods: {
    isLocked(teamAbbreviation) {
      return this.state.locks && this.state.locks[teamAbbreviation]
    },
  },

  created() {
    this.$bind("state", firestore.doc("public/state"))
  },
}
