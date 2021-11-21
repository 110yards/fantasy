<template>
  <div>
    <span v-if="progress" class="caption grey--text">{{ progress.remaining }} games left</span>
    <v-progress-linear v-if="progress" :value="progress.percent_complete" :reverse="reverse" />
  </div>
</template>

<script>
import { progress } from "../../../api/110yards/roster"

export default {
  name: "MatchupProgress",
  props: {
    leagueId: { type: String, required: true },
    roster: { type: Object, required: true },
    reverse: { type: Boolean, required: false, default: false },
  },

  data() {
    return {
      progress: null,
    }
  },

  computed: {
    currentUser() {
      return this.$store.state.currentUser
    },
  },

  methods: {
    async updateExternal() {
      if (!this.currentUser || !this.roster) return // can't hit this endpoint until we have a user

      if (this.$root.enableMatchupProgress) {
        this.progress = await progress(this.leagueId, this.roster.id)
      }
    },
  },

  watch: {
    roster: {
      immediate: true,
      handler(roster) {
        if (roster) {
          this.updateExternal()
        }
      },
    },

    currentUser: {
      immediate: true,
      handler(currentUser) {
        if (!currentUser) return

        this.updateExternal()
      },
    },
  },
}
</script>
