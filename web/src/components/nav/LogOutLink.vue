<template>
  <v-btn text to="#" @click="logOut">Log out</v-btn>
</template>

<script>
import { auth } from "@/modules/firebase"

export default {
  methods: {
    async logOut() {
      await auth.signOut()
      this.$router.replace("/")
    },
  },
}
</script>
