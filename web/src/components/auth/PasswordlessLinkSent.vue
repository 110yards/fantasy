<template>
  <v-card-text>
    <p class="text-left">
      A sign in link has been sent to {{ this.email }}, please check your email and click the link to log in.
    </p>
    <p><why-passwordless /></p>
  </v-card-text>
</template>

<script>
import WhyPasswordless from "./WhyPasswordless.vue"
export default {
  components: { WhyPasswordless },
  name: "PasswordlessLinkSent",
  props: {
    email: {
      type: String,
      required: true,
    },
  },
}
</script>
