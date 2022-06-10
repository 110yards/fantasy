<template>
  <div>
    <span v-if="progress" class="caption grey--text">{{ progress.remaining }} games left</span>
    <v-progress-linear v-if="progress" :value="progress.percent_complete" :reverse="reverse" />
  </div>
</template>

<script>
import { eventStatus } from "../../../api/110yards/constants"
import { progress } from "../../../api/110yards/roster"
import { firestore } from "../../../modules/firebase"

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
      remainingGames: null,
      completedGames: null,
    }
  },

  computed: {
    currentUser() {
      return this.$store.state.currentUser
    },

    season() {
      return this.$root.currentSeason
    },
  },

  methods: {
    async update() {
      if (!this.currentUser || !this.roster) return // can't hit this endpoint until we have a user

      if (this.$root.enableMatchupProgress) {
        this.progress = await progress(this.leagueId, this.roster.id)
      }
    },
  },

  watch: {
    completedGames: {
      immediate: true,
      handler(_) {
        this.update()
      },
    },

    currentUser: {
      immediate: true,
      handler(_) {
        this.update()
      },
    },

    roster: {
      immediate: true,
      handler(_) {
        this.update()
      },
    },
  },

  mounted() {
    let ref = firestore
      .collection(`season/${this.season}/game`)
      .where("event_status.event_status_id", "in", [eventStatus.Final, eventStatus.Cancelled])

    this.$bind("completedGames", ref)
  },
}
</script>
