<template>
  <v-card v-if="league">
    <v-card-subtitle class="subtitle mt-n10">
      You can use the notes to keep track of league information (eg: payouts, gentleman's rules). League notes are
      visible to all manager.
    </v-card-subtitle>

    <v-card-text>
      <v-form ref="form" @submit.prevent="submit()">
        <app-text-area v-model="form.notes" label="Notes" />

        <app-primary-button>Update</app-primary-button>
        <saved-indicator :saved="saved" />
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script>
import { firestore } from "../../modules/firebase"
import * as leagueService from "../../api/110yards/league"
import SavedIndicator from "../SavedIndicator"
import AppPrimaryButton from "../buttons/AppPrimaryButton.vue"
import { draftType } from "../../api/110yards/constants"
import AppTextArea from "../inputs/AppTextArea.vue"

export default {
  name: "league-options",
  components: {
    SavedIndicator,
    AppPrimaryButton,
    AppTextArea,
  },
  props: {
    league: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      form: {
        notes: null,
      },
      saved: false,
    }
  },
  computed: {},

  methods: {
    async submit() {
      let valid = await this.$refs.form.validate()
      if (!valid) return

      this.save()
    },
    async save() {
      let user = this.$store.state.currentUser
      let command = {
        league_id: this.league.id,
        notes: this.form.notes,
      }
      await leagueService.setNotes(user, this.league.id, command)
      this.saved = true
    },
  },
  watch: {
    league: {
      immediate: true,
      async handler(league) {
        if (league == null) return

        this.form.notes = league.notes
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
