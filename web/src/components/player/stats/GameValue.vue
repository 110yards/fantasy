<template>
  <td>
    {{ display }}
  </td>
</template>

<script>
export default {
  props: {
    value: { type: Number },
  },

  computed: {
    display() {
      return this.value != null && this.value != undefined ? this.value : 0
    },
  },
}
</script>
