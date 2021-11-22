<template>
  <v-snackbar v-model="visible" :timeout="timeout" :color="color">
    {{ message }}
    <template v-slot:action="{ attrs }">
      <v-btn text v-bind="attrs" @click="visible = false"> Close </v-btn>
    </template>
  </v-snackbar>
</template>

<style scoped>
.v-snack >>> .warning div,
.v-snack >>> .warning span {
  color: black !important;
}
</style>

<script>
import eventBus from "../modules/eventBus"
export default {
  name: "SnackBar",
  data() {
    return {
      visible: false,
      message: "",
      error: false,
      timeout: 5000,
      color: "info",
    }
  },
  created() {
    eventBus.$on("show-success", message => {
      this.message = message
      this.color = "success"
      this.visible = true
    })
    eventBus.$on("show-info", message => {
      this.message = message
      this.color = "info"
      this.visible = true
    })
    eventBus.$on("show-warning", message => {
      this.message = message
      this.color = "warning"
      this.visible = true
    })
    eventBus.$on("show-error", message => {
      this.message = message
      this.color = "error"
      this.visible = true
    })
  },
}
</script>
