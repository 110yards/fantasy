<template>
  <v-btn text to="/mod">Mod Tools <v-badge v-if="highlight" class="ml-2" dot color="green"></v-badge></v-btn>
</template>

<script>
export default {
  name: "ModLink",
  computed: {
    highlight() {
      return this.$root.highlightModTools
    },
  },
}
</script>
