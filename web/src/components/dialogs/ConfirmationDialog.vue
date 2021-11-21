<template>
  <v-dialog v-model="visible" :width="options.width" persistent>
    <v-card>
      <v-card-title class="header white--text">
        {{ options.title }}
      </v-card-title>

      <v-card-text class="mt-2 primary--text">
        {{ options.message }}
      </v-card-text>
      <v-divider></v-divider>

      <v-card-actions>
        <v-spacer></v-spacer>
        <app-secondary-button @click="no()">{{ $t("no") }}</app-secondary-button>
        <app-primary-button @click="yes()">{{ $t("yes") }}</app-primary-button>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import AppPrimaryButton from "./buttons/AppPrimaryButton.vue"
import AppSecondaryButton from "./buttons/AppSecondaryButton.vue"

export default {
  components: { AppPrimaryButton, AppSecondaryButton },
  name: "ConfirmationDialog",
  data() {
    return {
      visible: false,
      options: {
        width: 500,
        title: this.$t("confirm_action_title"),
        message: null,
      },
      resolve: null,
      reject: null,
    }
  },
  methods: {
    open(options) {
      this.visible = true
      this.options = Object.assign(this.options, options)
      return new Promise((resolve, reject) => {
        this.resolve = resolve
        this.reject = reject
      })
    },
    yes() {
      this.resolve(true)
      this.visible = false
    },
    no() {
      this.resolve(false)
      this.visible = false
    },
  },
  provide: function() {
    return { yes: this.yes, no: this.no }
  },
}
</script>
