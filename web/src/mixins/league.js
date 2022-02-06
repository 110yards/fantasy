import { firestore } from "../modules/firebase"

export default {
  data() {
    return {
      leagueScoringSettings: null,
      currentLeague: null,
    }
  },

  computed: {
    leagueId() {
      return "leagueId" in this.$route.params ? this.$route.params.leagueId : null
    },

    isCommissioner() {
      if (this.currentLeague == null || this.$store.state.currentUser == null) return false

      return this.currentLeague.commissioner_id == this.$store.state.currentUser.uid
    },
  },

  methods: {},

  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        if (leagueId) {
          let path = `league/${leagueId}/config/scoring`
          let ref = firestore.doc(path)
          this.$bind("leagueScoringSettings", ref)

          this.$bind("currentLeague", firestore.doc(`league/${leagueId}`))
        } else {
          if (this.leagueScoringSettings) {
            this.$unbind("leagueScoringSettings")
          }

          if (this.currentLeague) {
            this.$unbind("currentLeague")
          }
        }
      },
    },
  },
}
