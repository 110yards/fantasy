<template>
  <v-form ref="form" @submit.prevent="trySignup()">
    <app-text-field v-model="leagueId" label="League ID" required />

    <app-text-field v-model="password" label="Password" />

    <app-primary-button>Join</app-primary-button>
  </v-form>
</template>

<script>
import eventBus from "../../modules/eventBus"
import * as leagueService from "../../api/110yards/league"
import AppTextField from "../inputs/AppTextField.vue"
import AppPrimaryButton from "../buttons/AppPrimaryButton.vue"

export default {
  name: "join-private-form",
  components: {
    AppTextField,
    AppPrimaryButton,
  },
  data() {
    return {
      joining: false,
      failed: false,
      leagueId: null,
      password: null,
    }
  },
  computed: {
    currentUser() {
      return this.$store.state.currentUser
    },
  },
  methods: {
    async trySignup() {
      if (this.leagueId && this.currentUser) {
        this.joining = true

        let result = await leagueService.join(this.currentUser, this.leagueId, this.password)

        if (result.success) {
          this.$router.push({
            name: "league",
            params: { leagueId: this.leagueId },
          })
        }
      }
    },
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
  mounted: function () {
    this.password = this.$route.query.password
    this.leagueId = this.$route.params.joinId
  },
}
</script>
