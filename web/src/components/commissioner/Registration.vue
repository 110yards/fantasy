<template>
  <v-row>
    <v-col cols="12" class="registration-control">
      <div v-if="league.registration_closed">
        <p>
          Registration for this league has been closed, so no other managers may join.
        </p>
        <app-primary-button v-if="!leagueStarted" @click="reopenRegistration()">
          Re-open registration
        </app-primary-button>
      </div>
      <div v-if="!league.is_full && !league.registration_closed">
        <p>
          Registration for this league is open. To prevent new registrations, generate a schedule or click here:
        </p>
        <app-primary-button @click="closeRegistration()">
          Close registration
        </app-primary-button>
      </div>

      <start-draft :league="league" />
    </v-col>
    <v-col v-if="!leagueStarted && !league.registration_closed" md="6" cols="12" class="invite-options">
      <h4 v-if="enableInviteByEmail">Invite manager by email:</h4>
      <div v-if="enableInviteByEmail" class="form-inline">
        <div class="form-group">
          <v-text-field
            v-model="inviteEmail"
            solo-inverted
            dense
            :rules="inviteEmailRules"
            append-outer-icon="mdi-send"
            @click:append-outer="sendInvite()"
          />
        </div>
      </div>
      <h4 v-if="enableInviteByEmail">Or send this link:</h4>
      <h4 v-else>Invite link:</h4>
      <div class="form-inline">
        <div class="form-group">
          <v-text-field
            id="join-link"
            v-model="joinLink"
            solo-inverted
            dense
            readonly
            append-outer-icon="mdi-content-copy"
            @click:append-outer="copyJoinLink()"
          />
        </div>
      </div>
    </v-col>
    <v-col md="6" cols="12">
      <h4>League ID:</h4>
      <v-text-field
        v-model="league.id"
        id="league-id"
        solo-inverted
        dense
        readonly
        append-outer-icon="mdi-content-copy"
        @click:append-outer="copyLeagueId()"
      />
    </v-col>
  </v-row>
</template>

<script>
import router from "../../modules/router"
import * as leagueService from "../../api/110yards/league"
import { firestore } from "../../modules/firebase"
import AppPrimaryButton from "../buttons/AppPrimaryButton.vue"
import AppTextField from "../inputs/AppTextField.vue"
import validateEmail from "../../actions/validateEmail"
import StartDraft from "./StartDraft.vue"

export default {
  name: "registration",
  components: {
    AppPrimaryButton,
    AppTextField,
    StartDraft,
  },
  props: {
    league: Object,
    leagueStarted: {
      required: true,
      type: Boolean,
    },
  },
  data() {
    return {
      privateConfig: null,
      joinLink: null,
      inviteEmail: null,
      inviteEmailRules: [v => validateEmail(v)],
    }
  },
  computed: {
    password() {
      return this.privateConfig ? this.privateConfig.password : null
    },

    user() {
      return this.$store.state.currentUser
    },
    enableInviteByEmail() {
      return this.$root.enableInviteByEmail
    },
  },
  methods: {
    copyLeagueId() {
      let element = document.getElementById("league-id")
      element.focus()
      element.select()
      document.execCommand("copy")
    },
    copyJoinLink() {
      let element = document.getElementById("join-link")
      element.focus()
      element.select()
      document.execCommand("copy")
    },
    setJoinLink() {
      let params = { joinId: this.league.id }
      let query = {}

      if (this.password != null) {
        query = { password: this.privateConfig.password }
      }

      let route = router.resolve({
        name: "join-direct",
        params: params,
        query: query,
      })
      this.joinLink = `${window.location.origin}${route.href}`
    },
    async reopenRegistration() {
      await leagueService.openRegistration(this.user, this.league.id)
    },
    async closeRegistration() {
      await leagueService.closeRegistration(this.user, this.league.id)
    },
  },
  watch: {
    league: {
      immediate: true,
      handler(league) {
        if (league == null) return
        let ref = firestore
          .collection("league")
          .doc(league.id)
          .collection("config")
          .doc("private")
        this.$bind("privateConfig", ref)
      },
    },
    password: {
      immediate: true,
      handler(password) {
        this.setJoinLink()
      },
    },
  },
}
</script>

<style scoped>
.registration-control {
  padding-bottom: 2em;
}
</style>
