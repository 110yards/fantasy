<template>
  <v-btn v-if="link" text :href="link" target="_blank">Discord</v-btn>
</template>
<script>
export default {
  computed: {
    link() {
      return this.$root.officialDiscordLink
    },
  },
}
</script>
