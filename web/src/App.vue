<template>
  <v-app v-if="switchesLoaded">
    <app-header :siteOffline="siteOffline" />
    <v-main>
      <v-system-bar
        :class="systemBarClass"
        @click="clickMessage()"
        v-if="showMessage"
        height="auto"
        :color="siteMessage.color"
        class="pa-2"
      >
        {{ siteMessage.text }}
      </v-system-bar>
      <v-container v-if="!siteOffline" id="body" class="spacing-playground pa-1" fluid>
        <div class="container">
          <donate v-if="donateAtTop" />
          <router-view />
          <throbber />
          <div id="footer">
            <p>&copy; 2021 Michael Dryden</p>

            <donate v-if="donateAtBotton" />
          </div>
        </div>
      </v-container>
    </v-main>
    <snack-bar ref="snackBar" />
  </v-app>
</template>

<style>
.roster-name,
.trim {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.v-btn {
  text-transform: none !important;
  font-weight: normal !important;
}

.v-btn--active::before {
  opacity: 0 !important;
}
.v-btn--active:hover::before {
  opacity: 0.18 !important;
}

.v-card__title {
  word-break: unset;
}

#footer {
  padding-top: 2em;
  margin: auto;
  text-align: center;
  font-size: small;
  color: gray;
}

.link {
  cursor: pointer;
}
</style>

<script>
import Throbber from "./components/Throbber"
import AppHeader from "./components/header/AppHeader.vue"
import SnackBar from "./components/SnackBar.vue"
import SystemBar from "./components/SystemBar.vue"
import { firestore } from "./modules/firebase"
import * as api from "./api/110yards/root"
import Donate from "./components/Donate.vue"

export default {
  name: "App",
  components: {
    Throbber,
    AppHeader,
    SnackBar,
    SystemBar,
    Donate,
  },
  data() {
    return {
      siteMessage: null,
    }
  },
  computed: {
    switchesLoaded() {
      return this.$root.switchesLoaded
    },
    noProfile() {
      return this.$store.state.noProfile
    },
    showMessage() {
      return this.siteMessage != null && this.siteMessage.active
    },
    siteOffline() {
      return this.showMessage && this.siteMessage.is_offline_message === true
    },
    showMessageLink() {
      return this.showMessage && this.siteMessage.href !== null
    },
    systemBarClass() {
      return this.showMessageLink ? "link" : ""
    },

    isErrorPage() {
      let errorRoutes = ["error"]
      return errorRoutes.includes(this.$route.name)
    },

    donateAtTop() {
      return !this.isErrorPage && this.$root.showDonationLink && this.$route.name == "home"
    },

    donateAtBotton() {
      return !this.isErrorPage && this.$root.showDonationLink && this.$route.name != "home"
    },
  },

  methods: {
    clickMessage() {
      if (!this.showMessage || !this.showMessageLink) return

      window.location.href = this.siteMessage.href
    },

    async wakeApi() {
      api.status(true)
    },
  },

  watch: {
    noProfile: {
      immediate: true,
      handler(noProfile) {
        if (noProfile) {
          this.$router.push("complete-signup")
        }
      },
    },
  },

  created() {
    this.$bind("siteMessage", firestore.collection("public").doc("site_message"))
    this.wakeApi()
  },
}
</script>
