<template>
  <span> </span>
</template>

<script>
export default {
  props: {
    leagueId: {
      type: String,
      required: true,
    },

    rosterId: {
      type: String,
      required: true,
    },

    weekNumber: {
      required: true,
    },
  },

  data() {
    return {}
  },

  computed: {
    isCurrentWeek() {
      return this.$root.state.current_week == this.weekNumber
    },
  },

  methods: {
    configureReferences() {
      if (!this.leagueId || !this.rosterId || !this.weekNumber) return
    },
  },

  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        this.configureReferences()
      },
    },

    rosterId: {
      immediate: true,
      handler(rosterId) {
        this.configureReferences()
      },
    },
  },
}
</script>
