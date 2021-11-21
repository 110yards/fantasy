<template>
  <transition name="fade">
    <span v-if="saved" class="saved">Saved&nbsp;<i class="fas fa-check"></i></span>
  </transition>
</template>

<style scoped>
.saved {
  padding-left: 0.5em;
  padding-right: 0.5em;
  color: green;
}

.fade-enter-active {
  transition: opacity 0.5s;
}

.fade-enter {
  opacity: 0;
}
</style>

<script>
export default {
  name: "saved-indicator",
  props: {
    saved: Boolean,
  },
}
</script>
