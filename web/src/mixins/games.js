import { firestore } from "../modules/firebase"

export default {
  data() {
    return {
      games: null,
    }
  },

  computed: {
    gamesById() {
      if (!this.games) return

      return this.games.reduce((obj, item) => {
        obj[item.id] = item
        return obj
      }, {})
    },
  },

  created() {
    let season = process.env.VUE_APP_SEASON
    let gamesRef = firestore.collection(`season/${season}/game`)
    this.$bind("games", gamesRef)
  },
}
