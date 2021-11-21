<template>
  <v-card class="mx-auto" max-width="400px">
    <v-card-title>Create a new account</v-card-title>
    <v-card-text v-if="!linkSent">
      <p>
        <v-form ref="form" @submit.prevent="register">
          <app-text-field label="Display name" v-model="displayName" :rules="displayNameRules" required />
          <app-text-field label="Email" v-model="email" :rules="emailRules" required />
          <app-primary-button block>Register</app-primary-button>
        </v-form>
      </p>

      <p class="text-center">OR</p>

      <social class="text-center" />

      <p class="text-center">
        <router-link to="/forgotpassword">Forgot your password?</router-link>
      </p>
      <p class="text-center">
        Already have an account?
        <router-link to="/login">Sign In</router-link>
      </p>
    </v-card-text>

    <passwordless-link-sent :email="email" v-if="linkSent" />
  </v-card>
</template>

<script>
import Social from "../../components/auth/Social.vue"
import { register } from "../../api/110yards/user"
import AppTextField from "../../components/inputs/AppTextField.vue"
import AppPrimaryButton from "../../components/buttons/AppPrimaryButton.vue"
import AppPasswordField from "../../components/inputs/AppPasswordField.vue"
import eventBus from "../../modules/eventBus"
import sendSignInLink from "../../actions/sendSignInLink"
import { auth } from "../../modules/firebase"
import PasswordlessLinkSent from "../../components/auth/PasswordlessLinkSent.vue"
import validateEmail from "../../actions/validateEmail"

export default {
  name: "Register",
  components: {
    Social,
    AppTextField,
    AppPrimaryButton,
    AppPasswordField,
    PasswordlessLinkSent,
  },
  data() {
    return {
      displayName: "",
      displayNameRules: [v => !!v || "Display name is required"],
      email: "",
      emailRules: [v => validateEmail(v)],
      password: "",
      linkSent: false,
    }
  },
  methods: {
    async register() {
      let valid = this.$refs.form.validate()

      if (!valid) return
      let command = {
        display_name: this.displayName,
        email: this.email,
      }
      let result = await register(command)

      if (result.success) {
        await sendSignInLink(this.email, false)
        this.linkSent = true
      } else {
        eventBus.$emit("show-error", result.error)
      }
    },
  },
}
</script>
