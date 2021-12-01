<template>
  <span>{{ formatScore(projection) }}</span>
</template>

<script>
// import { playerProjection } from "../../api/110yards/projection"
import * as formatter from "../../modules/formatter"

export default {
  name: "PlayerProjection",
  props: {
    leagueId: { type: String, required: true },
    player: { type: Object },
  },

  data() {
    return {
      projection: null,
    }
  },

  methods: {
    formatScore() {
      return this.projection != null ? formatter.formatScore(this.projection) : "-"
    },

    async updateProjection() {
      if (!this.leagueId) return

      if (this.player) {
        this.projection = await playerProjection(this.leagueId, this.player.id)
      } else {
        this.projection = null
      }
    },
  },

  watch: {
    player: {
      immediate: true,
      handler(player) {
        this.updateProjection()
      },
    },
  },
}
</script>
