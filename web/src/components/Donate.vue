<template>
  <a v-if="message" href="https://www.buymeacoffee.com/mdryden">
    <v-alert dense icon="mdi-gift" type="success" v-bind:class="{ 'mt-2': !top }">
      {{ message }}
    </v-alert>
  </a>
</template>

<script>
export default {
  name: "Donate",

  props: {
    top: {
      type: Boolean,
      default: true,
    },
  },

  computed: {
    message() {
      return this.$root.donateMessage
    },
  },
}
</script>
