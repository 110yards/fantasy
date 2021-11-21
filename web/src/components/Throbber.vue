<template>
  <div class="throbber">
    <loading :is-full-page="true" :active="active" color="red" background-color="black" loader="spinner"></loading>
  </div>
</template>

<script>
import Loading from "vue-loading-overlay"
import "vue-loading-overlay/dist/vue-loading.css"
import eventBus from "../modules/eventBus"

export default {
  name: "throbber",
  props: {},
  data() {
    return {
      active: false,
      color: "red",
      backgroundColor: "red",
    }
  },
  components: {
    Loading,
  },
  created() {
    eventBus.$on("loading-start", () => {
      this.active = true
    })

    eventBus.$on("loading-stop", () => {
      this.active = false
    })
  },
}
</script>
