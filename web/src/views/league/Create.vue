<template>
  <v-card max-width="600px">
    <v-card-title>Create a fantasy league</v-card-title>
    <v-card-text>
      <v-form ref="form" @submit.prevent="save">
        <app-text-field label="League Name" v-model="leagueName" :rules="leagueNameRules" required />

        <label class="control-label">Make this league private?</label>
        <v-layout align-center
          ><v-simple-checkbox v-model="isPrivate" class="form-check-input" :ripple="false" />
          <span>Yes</span>
          <span class="text-caption ml-1"
            >(Private leagues are hidden from the listing, and require a password to join)</span
          >
        </v-layout>

        <app-text-field v-model="password" label="League Password" v-show="isPrivate" />

        <app-primary-button>Create</app-primary-button>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script>
import * as leagueService from "../../api/110yards/league"
import AppPrimaryButton from "../../components/buttons/AppPrimaryButton.vue"
import AppCheckBox from "../../components/inputs/AppCheckBox.vue"
import AppTextField from "../../components/inputs/AppTextField.vue"
import eventBus from "../../modules/eventBus"

export default {
  name: "create-league",
  components: { AppTextField, AppCheckBox, AppPrimaryButton },
  data() {
    return {
      leagueName: null,
      leagueNameRules: [v => !!v || "League name is required"],
      isPrivate: false,
      password: null,
    }
  },
  computed: {
    currentUser() {
      return this.$store.state.currentUser
    },
  },
  methods: {
    async save() {
      let valid = this.$refs.form.validate()

      if (!valid) return

      let league = {
        name: this.leagueName,
        private: this.isPrivate,
        password: this.password,
      }

      let result = await leagueService.create(this.currentUser, league)
      console.log(result)

      if (result && result.success) {
        this.$router.push({ name: "league", params: { leagueId: result.league.id } })
      }
    },
  },
}
</script>
