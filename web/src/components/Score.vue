<template>
  <span v-if="score != null">{{ formattedScore }}</span>
  <span v-else>-</span>
</template>

<script>
import { formatScore } from "../modules/formatter"

export default {
  name: "Score",
  props: {
    score: {
      type: Number,
      required: false,
    },
  },

  computed: {
    formattedScore() {
      let score = this.score == null || this.score == undefined ? 0 : this.score

      return formatScore(score)
    },
  },
}
</script>
