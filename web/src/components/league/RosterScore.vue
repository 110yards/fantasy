<template>
  <span> </span>
</template>

<script>
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
  },

  methods: {
    configurePlayersFor() {
      let positions = Object.values(this.roster.positions)
      let players = positions.filter(x => x.player).map(x => x.player)
      let playerIds = players.map(x => x.id)

      let path = `season/${this.season}/player/${this.position.player.id}/game` // TODO: figure this out - doesn't work, as the games are under the players
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
