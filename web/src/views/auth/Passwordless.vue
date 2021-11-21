<template>
  <v-card class="mx-auto" max-width="400px">
    <v-card-title>Complete sign in</v-card-title>
    <v-card-text>
      <p>
        <v-form ref="form" @submit.prevent="login">
          <app-text-field label="Email" v-model="email" :rules="emailRules" autocomplete="email" required />
          <app-primary-button block>Log in</app-primary-button>
        </v-form>
      </p>
      <p class="text-center"><why-passwordless /></p>
    </v-card-text>
  </v-card>
</template>

<script>
import validateEmail from "../../actions/validateEmail"
import WhyPasswordless from "../../components/auth/WhyPasswordless.vue"
import AppPrimaryButton from "../../components/buttons/AppPrimaryButton.vue"
import AppTextField from "../../components/inputs/AppTextField.vue"
import eventBus from "../../modules/eventBus"
import { auth } from "../../modules/firebase"
export default {
  components: { AppTextField, AppPrimaryButton, WhyPasswordless },
  name: "Passwordless",
  data() {
    return {
      email: "",
      emailRules: [v => validateEmail(v)],
    }
  },
  methods: {
    async login() {
      try {
        await auth.signInWithEmailLink(this.email, window.location.href)
        this.$router.push("/")
      } catch (error) {
        console.error(error)
        eventBus.$emit("show-error", error)
      }
    },
  },
  created() {
    let isSignin = auth.isSignInWithEmailLink(window.location.href)
    if (isSignin) {
      this.email = localStorage.getItem("emailForSignIn")
      if (this.email) this.login()
    }
  },
}
</script>
