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
      if (this.score == null || this.score == undefined) this.score = 0

      return formatScore(this.score)
    },
  },
}
</script>
