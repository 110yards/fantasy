<template>
  <section id="socialLogins">
    <v-btn @click="signInWithGoogle" class="google mb-2">
      <v-icon>mdi-google</v-icon>
      <v-divider vertical class="mx-4" />
      Continue with Google
    </v-btn>
  </section>
</template>

<style scoped>
.v-btn {
  width: 20em;
}

.v-btn >>> .v-btn__content {
  justify-content: left;
}

.v-btn.google {
  background-color: #dd4b39;
}

.v-btn.facebook {
  background-color: #3b5998;
}

.v-btn.twitter {
  background-color: #55acee;
}
</style>

<script>
import firebase from "firebase/app"
import eventBus from "../../modules/eventBus"

export default {
  name: "social",

  methods: {
    async signInWithGoogle() {
      let google = new firebase.auth.GoogleAuthProvider()
      await this.socialLogin(google)
    },

    async socialLogin(provider) {
      await firebase.auth().signInWithRedirect(provider)
    },
  },
  async mounted() {
    try {
      eventBus.$emit("loading-start")
      console.debug("loading-start")
      let result = await firebase.auth().getRedirectResult()
      if (result.credential) {
        this.$router.push("/")
      }
    } catch (exception) {
      switch (exception.code) {
        case "auth/popup-closed-by-user":
          break
        default:
          console.error(exception)
          eventBus.$emit("show-error", "Login failed " + exception.message)
      }
    } finally {
      eventBus.$emit("loading-stop")
    }
  },
}
</script>
