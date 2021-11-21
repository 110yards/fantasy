<template>
  <v-btn :to="to" color="default_button" :type="type" @click="$emit('click')">
    <slot />
  </v-btn>
</template>

<style scoped>
.v-btn.default_button {
  border: 1px solid !important;
  border-color: var(--v-default_button_border-base) !important;
}
</style>

<script>
export default {
  name: "AppPrimaryButton",
  props: {
    type: {
      type: String,
      required: false,
      default: "button",
    },
    to: {
      type: Object,
      required: false,
    },
  },
}
</script>
