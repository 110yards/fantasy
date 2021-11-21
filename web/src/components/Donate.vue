<template>
  <a v-if="message" href="https://www.buymeacoffee.com/mdryden">
    <v-alert dense icon="mdi-gift" type="success">
      {{ message }}
    </v-alert>
  </a>
</template>

<script>
export default {
  name: "Donate",

  computed: {
    message() {
      return this.$root.donateMessage
    },
  },
}
</script>
