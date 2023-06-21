import { firestore } from "../modules/firebase"

export default {
  data() {
    return {
      switches: null,
    }
  },
  methods: {
    getSwitch(key) {
      if (!this.switchesLoaded) return false

      if (this.enableAdminSwitchOverride && this.$store.state.isAdmin) {
        return true
      } else {
        return key in this.switches && this.switches[key]
      }
    },
  },
  computed: {
    switchesLoaded() {
      return this.switches != null
    },
    enableAdminSwitchOverride() {
      return this.switches.enable_admin_switch_override
    },
    enableDraft() {
      return this.getSwitch("enable_draft")
    },
    enableFacebookLogin() {
      return this.getSwitch("enable_facebook_login")
    },
    enableInviteByEmail() {
      return this.getSwitch("enable_invite_by_email")
    },
    enableLogin() {
      return this.getSwitch("enable_login")
    },
    enablePublicLeagues() {
      return this.getSwitch("enable_public_leagues")
    },
    enableTwitterLogin() {
      return this.getSwitch("enable_twitter_login")
    },
    enablePlayerLinks() {
      return this.getSwitch("enable_player_links")
    },
    enableProjections() {
      return this.getSwitch("enable_projections")
    },
    enableRelaxedIR() {
      return this.getSwitch("enable_relaxed_ir")
    },
    enableMatchupProgress() {
      return this.getSwitch("enable_matchup_progress")
    },
    showNewRosterUITip() {
      return this.getSwitch("show_new_roster_ui_tip")
    },
    showDonationLink() {
      return this.getSwitch("show_donation_link")
    },
    donateMessage() {
      if (!this.switchesLoaded) return false
      return this.switches.donate_message
    },
    enableDiscordIntegration() {
      return this.getSwitch("enable_discord_integration")
    },
    officialDiscordLink() {
      if (!this.switchesLoaded) return false
      return this.getSwitch("official_discord_link")
    },
  },
  created() {
    this.$bind("switches", firestore.collection("public").doc("switches"))
  },
}
