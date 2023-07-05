<template>
  <span v-if="position">{{ formattedScore }}</span>
</template>

<script>
import { firestore, rtdb } from "../../modules/firebase"
import { formatScore } from "../../modules/formatter"
import { calculate } from "../../modules/scoring"

export default {
  props: {
    position: {
      type: Object,
      required: false,
    },
    leagueId: {
      type: String,
      required: true,
    },
    weekNumber: {
      required: true,
    },
  },

  data() {
    return {
      liveScore: null,
      gameScore: null,
      gameStats: null,
    }
  },

  computed: {
    season() {
      return this.$root.currentSeason
    },

    // stats() {
    //   // some weird weeks will have teams playing two games.  We only ever score the first one.
    //   return this.games && this.games.length > 0 ? this.games[0] : null
    // },

    isCurrentWeek() {
      return this.weekNumber == this.$root.state.current_week
    },

    score() {
      if (this.isCurrentWeek) {
        return this.gameStats ? calculate(this.$root.leagueScoringSettings, this.gameStats) : 0
      } else {
        return this.position.game_score
      }
    },

    formattedScore() {
      return this.score != null ? formatScore(this.score) : "-"
    },
  },

  methods: {
    configureReferences() {
      if (!this.position || !this.position.player || !this.leagueId || !this.weekNumber) return
      if (!this.isCurrentWeek) return

      let gameId = this.$root.getGameIdForTeam(this.position.player.team_abbr)
      if (!gameId) return

      let path = `boxscores/${this.season}/${gameId}/player_stats/${this.position.player.player_id}`
      let ref = rtdb.ref(path)
      this.$rtdbBind("gameStats", ref)

      // let path = `season/${this.season}/player_game/`

      // let ref = firestore
      //   .collection(path)
      //   .where("player_id", "==", this.position.player.player_id)
      //   .where("week_number", "==", parseInt(this.weekNumber))
      //   .orderBy("game_id")
      //   .limit(1)

      // this.$bind("games", ref)
    },
  },

  watch: {
    position: {
      immediate: true,
      handler(position) {
        this.configureReferences()
      },
    },

    leagueId: {
      immediate: true,
      handler(leagueId) {
        this.configureReferences()
      },
    },

    weekNumber: {
      immediate: true,
      handler(weekNumber) {
        this.configureReferences()
      },
    },
  },
}
</script>
