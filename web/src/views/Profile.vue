<template>
  <v-row v-if="!isAnonymous">
    <v-col md="6" col="12">
      <v-form ref="form" @submit.prevent="submit()">
        <app-text-field v-model="userProfile.email" label="Email" readonly disabled />
        <app-text-field v-model="form.displayName" label="Display name" :rules="displayNameRules" required />

        <app-primary-button>Update</app-primary-button>
        <saved-indicator :saved="saved" />
      </v-form>
    </v-col>
  </v-row>
</template>

<script>
import AppPrimaryButton from "../components/buttons/AppPrimaryButton.vue"
import AppFormLabel from "../components/inputs/AppFormLabel.vue"
import AppTextField from "../components/inputs/AppTextField.vue"
import SavedIndicator from "../components/SavedIndicator.vue"
import { firestore } from "../modules/firebase"
import { updateProfile } from "../api/110yards/user"

export default {
  components: { AppTextField, AppFormLabel, AppPrimaryButton, SavedIndicator },
  name: "Profile",
  data() {
    return {
      saved: false,
      userProfile: {},
      form: {
        displayName: null,
      },
      displayNameRules: [v => !!v || "Display name is required"],
    }
  },
  computed: {
    isAnonymous() {
      return this.$store.state.isAnonymous
    },
    userId() {
      return this.isAnonymous ? "" : this.$store.state.uid
    },
  },

  methods: {
    submit() {
      let valid = this.$refs.form.validate()
      if (!valid) return

      this.save()
    },
    async save() {
      let command = {
        uid: this.userId,
        display_name: this.form.displayName,
      }

      await updateProfile(command)
      this.saved = true
    },
  },

  watch: {
    userId: {
      immediate: true,
      handler(userId) {
        if (!userId) return
        this.$bind("userProfile", firestore.collection("user").doc(userId))
      },
    },
    userProfile: {
      immediate: true,
      handler(userProfile) {
        this.form.displayName = userProfile.display_name
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
