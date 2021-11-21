import { firestore } from "../modules/firebase"

export default {
  data() {
    return {
      leagueScoringSettings: null,
    }
  },

  computed: {
    leagueId() {
      return "leagueId" in this.$route.params ? this.$route.params.leagueId : null
    },
  },

  methods: {},

  watch: {
    // leagueId: {
    //   immediate: true,
    //   handler(leagueId) {
    //     if (leagueId) {
    //       let path = `league/${leagueId}/config/scoring`
    //       let ref = firestore.doc(path)
    //       this.$bind("leagueScoringSettings", ref)
    //     } else {
    //       if (this.leagueScoringSettings) {
    //         this.$unbind("leagueScoringSettings")
    //       }
    //     }
    //   },
    // },
  },
}
