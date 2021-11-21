<template>
  <span>
    <router-link
      :to="{
        name: 'roster',
        params: { leagueId: leagueId, rosterId: roster.id },
      }"
      >{{ rosterName }}</router-link
    >
    <span v-if="shouldTrim">...</span>
  </span>
</template>

<script>
const trimLength = 10

export default {
  props: {
    leagueId: {
      type: String,
      required: true,
    },
    roster: {
      type: Object,
      required: true,
    },
    trim: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  computed: {
    rosterName() {
      if (!this.roster) return ""

      let name = this.roster.name

      if (this.shouldTrim) {
        name = name.substring(0, trimLength).trim()
      }

      return name
    },

    shouldTrim() {
      return this.trim && this.roster && this.roster.name.length > trimLength
    },
  },
}
</script>
