<template>
  <span v-if="position">{{ formattedScore }}</span>
</template>

<script>
import { firestore } from "../../modules/firebase"
import { formatScore } from "../../modules/formatter"
import { playerScore } from "../../api/110yards/score"

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
    scoreboard: { required: false },
  },

  data() {
    return {
      liveScore: null,
      gameScore: null,
    }
  },

  computed: {
    season() {
      return process.env.VUE_APP_SEASON
    },

    isCurrentWeek() {
      return this.weekNumber == this.$root.state.current_week
    },

    score() {
      if (!this.scoreboard) return null

      if (this.liveScore != null) {
        for (let gameId in this.liveScore.game_scores) {
          if (gameId in this.scoreboard.games) {
            return this.liveScore.game_scores[gameId].total_score
          }
        }

        return 0.0
      }

      return this.gameScore
    },

    formattedScore() {
      return this.score != null ? formatScore(this.score) : "-"
    },
  },

  methods: {
    configureReferences() {
      if (!this.position || !this.position.player || !this.leagueId || !this.weekNumber) return

      if (this.isCurrentWeek) {
        let path = `league/${this.leagueId}/player_score/${this.position.player.id}`
        let ref = firestore.doc(path)

        this.$bind("liveScore", ref)
      } else {
        this.gameScore = this.position.game_score
      }
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
