<template>
  <div>
    <!-- TODO: drawer links -->
    <v-app-bar app color="header" dark short>
      <v-app-bar-nav-icon class="hidden-md-and-up" @click.stop="showDrawer = !showDrawer"></v-app-bar-nav-icon>

      <!-- Desktop -->
      <home-link class="hidden-sm-and-down" />
      <league-link v-if="!siteOffline && hasLeague" class="hidden-sm-and-down" :leagueId="leagueId" />
      <roster-link v-if="!siteOffline && hasRoster" class="hidden-sm-and-down" :leagueId="leagueId" :userId="userId" />
      <players-link v-if="!siteOffline && hasLeague" class="hidden-sm-and-down" :leagueId="leagueId" />

      <v-spacer class="hidden-sm-and-down" />

      <profile-link v-if="!isAnonymous" class="hidden-sm-and-down" />
      <support-link class="hidden-sm-and-down" />
      <faq-link class="hidden-sm-and-down" />
      <admin-link v-if="isAdmin" class="hidden-sm-and-down" />
      <log-in-link v-if="isAnonymous" class="hidden-sm-and-down" />
      <log-out-link v-if="!isAnonymous" class="hidden-sm-and-down" />

      <!-- Mobile -->
      <v-spacer class="hidden-md-and-up" />
      <home-link class="hidden-md-and-up" />
    </v-app-bar>

    <v-navigation-drawer v-model="showDrawer" color="header" app left temporary>
      <v-list nav dense>
        <v-list-item>
          <v-list-item-title> </v-list-item-title>
        </v-list-item>
        <v-list-item v-if="!siteOffline && !isAnonymous">
          <v-list-item-content>
            <profile-link />
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="!siteOffline && hasLeague">
          <v-list-item-content>
            <league-link :leagueId="leagueId" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="!siteOffline && hasRoster">
          <v-list-item-content>
            <roster-link :leagueId="leagueId" :userId="userId" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="!siteOffline && hasLeague">
          <v-list-item-content>
            <players-link :leagueId="leagueId" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <support-link />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <faq-link />
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="isAdmin">
          <v-list-item-content>
            <admin-link />
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="isAnonymous">
          <v-list-item-content>
            <log-in-link />
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="!isAnonymous">
          <v-list-item-content>
            <log-out-link />
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
  </div>
</template>

<style scoped>
.v-application a {
  color: rgba(255, 255, 255, 0.5);
}
</style>

<script>
import AdminLink from "./nav/AdminLink.vue"
import FaqLink from "./nav/FaqLink.vue"
import HomeLink from "./nav/HomeLink.vue"
import LeagueLink from "./nav/LeagueLink.vue"
import LogInLink from "./nav/LogInLink.vue"
import LogOutLink from "./nav/LogOutLink.vue"
import PlayersLink from "./nav/PlayersLink.vue"
import ProfileLink from "./nav/ProfileLink.vue"
import RosterLink from "./nav/RosterLink.vue"
import SupportLink from "./nav/SupportLink.vue"

export default {
  components: {
    HomeLink,
    LeagueLink,
    RosterLink,
    PlayersLink,
    FaqLink,
    AdminLink,
    LogInLink,
    LogOutLink,
    SupportLink,
    ProfileLink,
  },
  name: "AppHeader",
  props: {
    siteOffline: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      visible: false,
      rosterId: null,
      showDrawer: false,
    }
  },
  computed: {
    isAnonymous() {
      return this.$store.state.isAnonymous
    },
    username() {
      return this.isAnonymous ? "" : this.$store.state.currentUser.displayName
    },
    userId() {
      return this.isAnonymous ? "" : this.$store.state.uid
    },
    leagueId() {
      return this.$store.state.currentLeagueId
    },
    isAdmin() {
      return this.$store.state.isAdmin
    },
    hasLeague() {
      return this.leagueId
    },
    hasRoster() {
      return this.leagueId && this.userId
    },
  },
}
</script>
