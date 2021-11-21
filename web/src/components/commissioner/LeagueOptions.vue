<template>
  <v-row>
    <v-col md="6" cols="12">
      <v-form ref="form" @submit.prevent="submit()">
        <app-text-field v-model="form.name" label="League name" :rules="leagueNameRules" required />

        <div v-if="!leagueStarted">
          <app-form-label>Make this league private?</app-form-label>

          <v-layout align-center class="mb-8"
            ><v-simple-checkbox v-model="form.isPrivate" class="form-check-input" :ripple="false" />
            <span>Yes</span>
          </v-layout>

          <app-text-field v-model="form.password" label="League password" v-show="form.isPrivate" />

          <app-select v-model="form.draft_type" label="Draft type" :items="draftTypes" />
        </div>

        <div v-else>
          <p>
            <app-form-label>Private league: {{ form.isPrivate ? "Yes" : "No" }}</app-form-label>
          </p>
          <p v-show="form.isPrivate">
            <app-form-label>League password: {{ form.password }}</app-form-label>
          </p>
          <p>
            <app-form-label>Draft type: {{ draftTypeText }}</app-form-label>
          </p>
        </div>

        <app-primary-button>Update</app-primary-button>
        <saved-indicator :saved="saved" />
      </v-form>
    </v-col>
  </v-row>
</template>

<script>
import { firestore } from "../../modules/firebase"
import * as leagueService from "../../api/110yards/league"
import SavedIndicator from "../SavedIndicator"
import AppTextField from "../inputs/AppTextField.vue"
import AppSelect from "../inputs/AppSelect.vue"
import AppFormLabel from "../inputs/AppFormLabel.vue"
import AppPrimaryButton from "../buttons/AppPrimaryButton.vue"
import { draftType } from "../../api/110yards/constants"

export default {
  name: "league-options",
  components: {
    SavedIndicator,
    AppTextField,
    AppSelect,
    AppFormLabel,
    AppPrimaryButton,
  },
  props: {
    league: Object,
    leagueStarted: Boolean,
  },
  data() {
    return {
      leagueNameRules: [v => !!v || "League name is required"],
      form: {
        name: null,
        isPrivate: false,
        password: null,
        draft_type: null,
      },
      saved: false,
      draftTypes: [
        // { text: "Auction", value: "auction" },
        { text: "Snake", value: "snake" },
        { text: "Commissioner", value: "commissioner" },
      ],
    }
  },
  computed: {
    draftTypeText() {
      switch (this.form.draft_type) {
        case draftType.Auction:
          return "Auction"
        case draftType.Snake:
          return "Snake"
        case draftType.Commissioner:
          return "Commissioner"
        default:
          return ""
      }
    },
  },
  methods: {
    submit() {
      let valid = this.$refs.form.validate()
      if (!valid) return

      this.save()
    },
    async save() {
      let user = this.$store.state.currentUser
      let options = {
        name: this.form.name,
        private: this.form.isPrivate,
        password: this.form.isPrivate ? this.form.password : null,
        draft_type: this.form.draft_type,
      }
      await leagueService.update(user, this.league.id, options)
      this.saved = true
    },
  },
  watch: {
    league: {
      immediate: true,
      async handler(league) {
        if (league == null) return

        let privateSettings = (
          await firestore
            .collection("league")
            .doc(league.id)
            .collection("config")
            .doc("private")
            .get()
        ).data()

        this.form.name = league.name
        this.form.isPrivate = league.private
        this.form.password = privateSettings.password
        this.form.draft_type = league.draft_type
      },
    },
    form: {
      deep: true,
      handler(form) {
        this.saved = false
      },
    },
  },
}
</script>
