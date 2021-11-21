<template>
  <v-card class="mx-auto" max-width="400px">
    <v-card-title>Join league</v-card-title>
    <v-card-text>
      <join-private-form :joinId="joinId" :password="password" />
    </v-card-text>
  </v-card>
</template>

<script>
import JoinPrivateForm from "../../components/league/JoinPrivateForm.vue"
import * as leagueService from "../../api/110yards/league"
import eventBus from "../../modules/eventBus"

export default {
  name: "join-direct",
  props: {
    joinId: String,
  },
  components: {
    JoinPrivateForm,
  },
  computed: {
    currentUser() {
      return this.$store.state.currentUser
    },
    password() {
      return this.$route.query.password
    },
  },
  methods: {
    // async trySignup() {
    //   if (!this.joining && this.joinId && this.currentUser) {
    //     this.joining = true
    //     let result = await leagueService.join(this.currentUser, this.joinId, this.password)
    //     if (result.success) {
    //       alert("success")
    //     } else {
    //       eventBus.$emit("show-error", result.error)
    //     }
    //   }
    // },
  },
  watch: {
    joinId: {
      immediate: true,
      async handler(joinId) {
        this.leagueId = joinId
      },
    },
    currentUser: {
      immediate: true,
      async handler(currentUser) {
        //await this.trySignup()
      },
    },
  },
  mounted() {},
}
</script>
