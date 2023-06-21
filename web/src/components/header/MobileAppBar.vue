<template>
  <div>
    <v-app-bar app color="header" dark short>
      <v-app-bar-nav-icon @click.stop="showDrawer = !showDrawer"></v-app-bar-nav-icon>

      <v-spacer />
      <home-link />
    </v-app-bar>
    <v-navigation-drawer v-model="showDrawer" color="header" app left temporary>
      <v-list nav dense>
        <!-- spacer -->
        <v-list-item>
          <v-list-item-title> </v-list-item-title>
        </v-list-item>

        <!-- league -->
        <v-list-group v-if="hasLeague" :value="showLeagueSubMenu">
          <template v-slot:activator>
            <v-list-item-content>
              <v-list-item-title>
                <league-link :leagueId="leagueId" class="nav-primary" />
              </v-list-item-title>
            </v-list-item-content>
          </template>

          <!-- league sub menu -->
          <v-list-item class="ml-4">
            <v-list-item-title
              ><v-btn
                class="nav-secondary"
                text
                small
                :to="{ name: 'league-settings', params: { leagueId: leagueId } }"
              >
                Scoring
              </v-btn>
            </v-list-item-title>
          </v-list-item>

          <v-list-item class="ml-4">
            <v-list-item-title>
              <v-btn class="nav-secondary" text small :to="{ name: 'league-schedule', params: { leagueId: leagueId } }">
                Schedule
              </v-btn>
            </v-list-item-title>
          </v-list-item>

          <v-list-item v-if="isCommissioner || isAdmin" class="ml-4">
            <v-list-item-title>
              <v-btn class="nav-secondary" small text :to="{ name: 'commissioner', params: { leagueId: leagueId } }">
                Commissioner
              </v-btn>
            </v-list-item-title>
          </v-list-item>

          <v-list-item v-if="isAdmin" class="ml-4">
            <v-list-item-title>
              <v-btn class="nav-secondary" small text :to="{ name: 'league-admin', params: { leagueId: leagueId } }">
                Admin
              </v-btn></v-list-item-title
            >
          </v-list-item>

          <v-list-item class="ml-4" v-if="hasNotes">
            <v-list-item-title>
              <v-btn class="nav-secondary" text small :to="{ name: 'league-notes', params: { leagueId: leagueId } }">
                Notes
              </v-btn>
            </v-list-item-title>
          </v-list-item>
        </v-list-group>

        <!-- my team-->
        <v-list-item v-if="hasRoster">
          <v-list-item-content>
            <v-list-item-title>
              <roster-link :leagueId="leagueId" :userId="userId" class="nav-primary" />
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <!-- players -->
        <v-list-item v-if="hasLeague">
          <v-list-item-content>
            <v-list-item-title>
              <players-link :leagueId="leagueId" class="nav-primary" />
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <!-- profile link -->
        <v-list-item v-if="!isAnonymous">
          <v-list-item-content>
            <v-list-item-title>
              <profile-link class="nav-primary" />
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <!-- support -->
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title>
              <support-link class="nav-primary" />
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <!-- faq -->
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title>
              <faq-link class="nav-primary" />
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <!-- admin -->
        <v-list-item v-if="isAdmin">
          <v-list-item-content>
            <v-list-item-title>
              <admin-link class="nav-primary" />
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <!-- discord -->
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title>
              <discord-link class="nav-primary" />
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <!-- log in -->
        <v-list-item v-if="isAnonymous">
          <v-list-item-content>
            <v-list-item-title>
              <log-in-link class="nav-primary" />
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <!-- log out -->
        <v-list-item v-if="!isAnonymous">
          <v-list-item-content>
            <v-list-item-title>
              <log-out-link class="nav-primary" />
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
  </div>
</template>

<style scoped>
.nav-primary >>> * {
  color: rgba(255, 255, 255, 0.5);
}
.nav-secondary {
  color: rgba(255, 255, 255, 0.5);
}

.v-list-group >>> .v-icon {
  color: rgba(255, 255, 255, 0.5);
}
</style>

<script>
import AdminLink from "../nav/AdminLink.vue"
import DiscordLink from "../nav/DiscordLink.vue"
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
    DiscordLink,
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
    hasNotes: { required: true },
  },

  data() {
    return {
      showDrawer: false,
    }
  },

  computed: {
    showLeagueSubMenu() {
      switch (this.$route.name) {
        case "league":
        case "league-settings":
        case "league-schedule":
        case "commissioner":
        case "league-admin":
          return true

        default:
          return false
      }
    },
  },
}
</script>
