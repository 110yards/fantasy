<template>
  <v-card class="mx-auto" max-width="400px">
    <v-card-title>{{ title }}</v-card-title>
    <v-card-text v-if="!linkSent && enableLogin">
      <p>
        <v-form ref="form" @submit.prevent="login">
          <app-text-field label="Email" v-model="email" :rules="emailRules" autocomplete="email" required />
          <app-primary-button block>Send login link</app-primary-button>
        </v-form>
      </p>
      <p class="text-center"><why-passwordless /></p>

      <p class="text-center">OR</p>

      <social class="text-center" />

      <p class="text-center">
        Not signed up yet?
        <router-link to="/signup">Sign Up</router-link>
      </p>
    </v-card-text>
    <v-card-text v-if="linkSent">
      <p class="text-left">
        A sign in link has been sent to {{ this.email }}, please check your email and click the link to log in.
      </p>
      <p><why-passwordless /></p>
    </v-card-text>

    <v-card-text v-if="!enableLogin">
      <p class="text-left">
        Logging in to the site is currently disabled, please try again later.
      </p>
    </v-card-text>
  </v-card>
</template>

<style scoped>
#socialLogins {
  margin-bottom: 1rem;
}
</style>

<script>
import sendSignInLink from "../../actions/sendSignInLink"
import AppPrimaryButton from "../../components/buttons/AppPrimaryButton.vue"
import AppTextField from "../../components/inputs/AppTextField.vue"
import Social from "../../components/auth/Social.vue"
import AppPasswordField from "../../components/inputs/AppPasswordField.vue"
import WhyPasswordless from "../../components/auth/WhyPasswordless.vue"
import validateEmail from "../../actions/validateEmail"
import eventBus from "../../modules/eventBus"

export default {
  name: "login",
  props: {
    returnUrl: String,
  },
  components: {
    Social,
    AppTextField,
    AppPrimaryButton,
    AppPasswordField,
    WhyPasswordless,
  },
  data() {
    return {
      linkSent: false,
      email: "",
      emailRules: [v => validateEmail(v)],
    }
  },
  computed: {
    title() {
      return this.linkSent ? "Link sent" : "Log in to your account"
    },
    enableLogin() {
      return this.$root.enableLogin
    },
  },
  methods: {
    async login() {
      try {
        eventBus.$emit("loading-start")
        let valid = this.$refs.form.validate()
        if (!valid) return
        this.linkSent = await sendSignInLink(this.email, true)
      } finally {
        eventBus.$emit("loading-stop")
      }
    },
  },
  submit() {
    if (this.$refs.form.checkValidity()) {
      this.login()
    } else {
      this.$refs.form.reportValidity()
    }
  },
}
</script>
