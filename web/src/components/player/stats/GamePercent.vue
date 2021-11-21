<template>
  <td>
    {{ percent }}
  </td>
</template>

<script>
export default {
  props: {
    attempts: { type: Number },
    successes: { type: Number },
  },

  computed: {
    percent() {
      if (!this.attempts) return (0).toFixed(1)

      return ((this.successes * 100) / this.attempts).toFixed(1)
    },
  },
}
</script>
