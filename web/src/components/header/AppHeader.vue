<template>
  <div>
    <desktop-app-bar
      class="hidden-sm-and-down"
      v-if="!siteOffline"
      :hasLeague="hasLeague"
      :hasRoster="hasRoster"
      :isAdmin="isAdmin"
      :isCommissioner="isCommissioner"
      :isAnonymous="isAnonymous"
      :leagueId="leagueId"
      :userId="userId"
      :username="username"
    />

    <mobile-app-bar
      class="hidden-md-and-up"
      v-if="!siteOffline"
      :hasLeague="hasLeague"
      :hasRoster="hasRoster"
      :isAdmin="isAdmin"
      :isCommissioner="isCommissioner"
      :isAnonymous="isAnonymous"
      :leagueId="leagueId"
      :userId="userId"
      :username="username"
    />
  </div>
</template>

<script>
import AdminLink from "../nav/AdminLink.vue"
import FaqLink from "../nav/FaqLink.vue"
import HomeLink from "../nav/HomeLink.vue"
import LeagueLink from "../nav/LeagueLink.vue"
import LogInLink from "../nav/LogInLink.vue"
import LogOutLink from "../nav/LogOutLink.vue"
import PlayersLink from "../nav/PlayersLink.vue"
import ProfileLink from "../nav/ProfileLink.vue"
import RosterLink from "../nav/RosterLink.vue"
import SupportLink from "../nav/SupportLink.vue"
import DesktopAppBar from "./DesktopAppBar.vue"
import MobileAppBar from "./MobileAppBar.vue"

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
    DesktopAppBar,
    MobileAppBar,
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
    isCommissioner() {
      return this.$root.isCommissioner
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
