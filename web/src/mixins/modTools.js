import { firestore } from "../modules/firebase"

export default {
  data() {
    return {
      playerApprovals: null,
    }
  },

  computed: {
    highlightModTools() {
      return this.isMod && this.anyPlayerApprovals
    },

    anyPlayerApprovals() {
      return this.playerApprovals != null && this.playerApprovals.length > 0
    },

    isAdmin() {
      return this.$store.state.isAdmin
    },

    isMod() {
      return this.$store.state.isAdmin || this.$store.state.isMod
    },
  },

  methods: {},

  watch: {
    isMod: {
      handler: function (isMod) {
        if (!isMod) return

        let ref = firestore.collection("mod/approvals/players").limit(1)
        this.$bind("playerApprovals", ref)
      },
      immediate: true,
    },
  },
}
