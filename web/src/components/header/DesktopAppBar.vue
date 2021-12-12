<template>
  <v-app-bar app color="header" dark extension-height="30">
    <home-link />
    <league-link v-if="hasLeague" :leagueId="leagueId" class="nav-primary" />
    <roster-link v-if="hasRoster" :leagueId="leagueId" :userId="userId" class="nav-primary" />
    <players-link v-if="hasLeague" :leagueId="leagueId" class="nav-primary" />

    <v-spacer />

    <profile-link v-if="!isAnonymous" class="nav-primary" />
    <support-link class="nav-primary" />
    <faq-link class="nav-primary" />
    <admin-link v-if="isAdmin" class="nav-primary" />
    <log-in-link v-if="isAnonymous" class="nav-primary" />
    <log-out-link v-if="!isAnonymous" class="nav-primary" />

    <template v-slot:extension v-if="hasLeague">
      <v-btn
        class="ml-11 mt-n3 nav-secondary"
        text
        small
        :to="{ name: 'league-settings', params: { leagueId: league.id } }"
      >
        Scoring
      </v-btn>
      <v-btn class="mt-n3 nav-secondary" text small :to="{ name: 'league-schedule', params: { leagueId: leagueId } }"
        >Schedule</v-btn
      >

      <v-btn
        class="mt-n3 nav-secondary"
        small
        v-if="isCommissioner || isAdmin"
        text
        :to="{ name: 'commissioner', params: { leagueId: leagueId } }"
      >
        Commissioner
      </v-btn>

      <v-btn
        class="mt-n3 nav-secondary"
        small
        v-if="isAdmin"
        text
        :to="{ name: 'league-admin', params: { leagueId: leagueId } }"
      >
        Waiver Results
      </v-btn>
    </template>
  </v-app-bar>
</template>

<style scoped>
.nav-primary {
  color: rgba(255, 255, 255, 0.5);
}
.nav-secondary {
  color: rgba(255, 255, 255, 0.5);
}
</style>

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

  props: {
    isAnonymous: { required: true },
    username: { required: true },
    userId: { required: true },
    leagueId: { required: true },
    isAdmin: { required: true },
    isCommissioner: { required: true },
    hasLeague: { required: true },
    hasRoster: { required: true },
  },

  computed: {
    league() {
      return this.$root.currentLeague
    },
  },
}
</script>
