<template>
  <v-btn :to="to" color="primary_button" :type="type" :block="block" @click="$emit('click')">
    <slot />
  </v-btn>
</template>

<style scoped>
.v-btn.primary_button {
  border: 1px solid !important;
  border-color: var(--v-primary_button_border-base) !important;
}
</style>

<script>
export default {
  name: "AppPrimaryButton",
  props: {
    type: {
      type: String,
      required: false,
      default: "submit",
    },
    to: {
      type: Object,
      required: false,
    },
    block: {
      type: Boolean,
      required: false,
    },
  },
}
</script>
