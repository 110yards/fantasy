<template>
  <td>
    {{ average }}
  </td>
</template>

<script>
export default {
  props: {
    attempts: { type: Number },
    yards: { type: Number },
  },

  computed: {
    average() {
      if (!this.attempts) return

      return (this.yards / this.attempts).toFixed(1)
    },
  },
}
</script>
