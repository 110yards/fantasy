<template>
  <span>{{ score }} </span>
</template>

<script>
import { firestore } from "../../modules/firebase"
import { calculate, calculateMultiple } from "../../modules/scoring"

export default {
  props: {
    roster: {
      type: Object,
      required: true,
    },

    // TODO: figure out how to highlight.  Can I pass back an event with the calculated score, and highlight
    // one level higher, when I have both scores?
    // opponent: {
    //   type: Object,
    //   required: false,
    // },

    weekNumber: {
      required: true,
    },
  },

  data() {
    return {
      playersFor: null,
      // playersAgainst: null,
    }
  },

  computed: {
    season() {
      return this.$root.currentSeason
    },

    isCurrentWeek() {
      return this.$root.state.current_week == this.weekNumber
    },

    score() {
      return this.playersFor ? calculateMultiple(this.$root.leagueScoringSettings, this.playersFor) : 0 // TODO: not working
    },
  },

  methods: {
    configurePlayersFor() {
      let positions = Object.values(this.roster.positions)
      let players = positions.filter(x => x.player).map(x => x.player)
      let playerIds = players.map(x => x.id)

      let path = `season/${this.season}/player_game/`
      let ref = firestore
        .collection(path)
        .where("week_number", "==", parseInt(this.weekNumber))
        .where("player_id", "in", playerIds)

      this.$bind("playersFor", ref)
    },
  },

  watch: {
    roster: {
      immediate: true,
      handler(roster) {
        if (roster) this.configurePlayersFor()
      },
    },
  },
}
</script>
