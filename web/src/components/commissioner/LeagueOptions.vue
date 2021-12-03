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

        <div v-if="enableDiscordIntegration">
          <app-form-label>
            <span>Enable discord notifications?</span>
            <v-btn icon class="ml-2" href="https://github.com/mdryden/110yards/wiki#discord" target="_blank"
              ><v-icon>mdi-help-circle</v-icon></v-btn
            >
          </app-form-label>

          <v-layout align-center class="mb-2"
            ><v-simple-checkbox v-model="form.enable_discord_notifications" class="form-check-input" :ripple="false" />
            <span>Yes</span>
          </v-layout>
        </div>

        <div v-if="enableDiscordIntegration && form.enable_discord_notifications" class="ml-8">
          <app-text-field
            v-model="form.discord_webhook_url"
            label="Discord webhook URL"
            :required="form.enable_discord_notifications"
            :rules="discordWebhookRules"
          />

          <app-form-label>
            <span>Send discord notifications for:</span>
          </app-form-label>
          <v-layout align-center class="ml-2 mb-2 mt-2">
            <v-simple-checkbox v-model="form.notifications_draft" class="form-check-input" :ripple="false" />
            <span>Draft events</span>
          </v-layout>

          <v-layout align-center class="ml-2 mb-2"
            ><v-simple-checkbox v-model="form.notifications_transactions" class="form-check-input" :ripple="false" />
            <span>Transactions</span>
          </v-layout>

          <v-layout align-center class="ml-2 mb-2"
            ><v-simple-checkbox v-model="form.notifications_waivers" class="form-check-input" :ripple="false" />
            <span>Waivers</span>
          </v-layout>

          <v-layout align-center class="ml-2 mb-2"
            ><v-simple-checkbox v-model="form.notifications_end_of_week" class="form-check-input" :ripple="false" />
            <span>End of week</span>
          </v-layout>

          <app-default-button v-if="form.discord_webhook_url" class="mb-4" @click="testDiscordIntegration()"
            >Send a test notification</app-default-button
          >
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
import AppDefaultButton from "../buttons/AppDefaultButton.vue"

export default {
  name: "league-options",
  components: {
    SavedIndicator,
    AppTextField,
    AppSelect,
    AppFormLabel,
    AppPrimaryButton,
    AppDefaultButton,
  },
  props: { league: Object, leagueStarted: Boolean },
  data() {
    return {
      leagueNameRules: [v => !!v || "League name is required"],
      discordWebhookRules: [v => (this.form.enable_discord_notifications && !!v) || "Discord webhook url is required"],
      form: {
        name: null,
        isPrivate: false,
        password: null,
        draft_type: null,
        enable_discord_notifications: false,
        discord_webhook_url: null,
        notifications_draft: true,
        notifications_end_of_week: true,
        notifications_transactions: true,
        notifications_waivers: true,
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

    enableDiscordIntegration() {
      return this.$root.enableDiscordIntegration
    },
  },
  methods: {
    async submit() {
      let valid = await this.$refs.form.validate()
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
        enable_discord_notifications: this.form.enable_discord_notifications,
        discord_webhook_url: this.form.discord_webhook_url,
        notifications_draft: this.form.notifications_draft,
        notifications_end_of_week: this.form.notifications_end_of_week,
        notifications_transactions: this.form.notifications_transactions,
        notifications_waivers: this.form.notifications_waivers,
      }
      // alert(JSON.stringify(options))
      await leagueService.update(user, this.league.id, options)
      this.saved = true
    },

    async testDiscordIntegration() {
      await leagueService.testDiscord(this.league.id, this.form.discord_webhook_url)
    },
  },
  watch: {
    league: {
      immediate: true,
      async handler(league) {
        if (league == null) return

        let privateSettings = (
          await firestore.collection("league").doc(league.id).collection("config").doc("private").get()
        ).data()

        this.form.name = league.name
        this.form.isPrivate = league.private
        this.form.password = privateSettings.password
        this.form.draft_type = league.draft_type
        this.form.enable_discord_notifications = league.enable_discord_notifications || false
        this.form.discord_webhook_url = privateSettings.discord_webhook_url || null
        this.form.notifications_draft = league.notifications_draft || false
        this.form.notifications_end_of_week = league.notifications_end_of_week || false
        this.form.notifications_transactions = league.notifications_transactions || false
        this.form.notifications_waivers = league.notifications_waivers || false
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
