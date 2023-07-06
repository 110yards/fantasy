<template>
  <div>
    <!-- <v-row v-if="nextGame && nextGame.teams.away && nextGame.teams.home">
      <v-col>Next game: {{ nextGame.teams.away }}</v-col>
    </v-row> -->
    <v-row>
      <v-col cols="12" md="8">
        <focus-game class="d-md-none" />
        <v-card>
          <v-card-title class="text-h4">110 yards</v-card-title>
          <v-card-subtitle class="subtitle"> {{ randomSlogan }}</v-card-subtitle>

          <v-card-text v-if="hasLeagues">
            <h3>My Teams - Week {{ weekNumber }}</h3>
            <v-col cols="12">
              <div v-for="league in leagues" :key="league.leagueId">
                <v-row>
                  <v-col cols="12" class="title">
                    <router-link
                      :to="{
                        name: 'league',
                        params: { leagueId: league.id },
                      }"
                      >{{ league.league_name }}</router-link
                    >
                  </v-col>
                </v-row>

                <matchup-preview
                  class="d-flex mb-10 matchup"
                  :leagueId="league.id"
                  :weekNumber="weekNumber"
                  :matchup="league.matchup"
                />
              </div>
            </v-col>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="4" class="d-none d-md-flex" v-if="hasLeagues">
        <scoreboard />
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title v-if="!hasLeagues">Join a league or create a new one!</v-card-title>
          <v-card-text>
            <p>
              <app-primary-button :to="{ name: 'join-league' }">Join a league</app-primary-button>&nbsp;or
              <app-default-button :to="{ name: 'create-league' }"> Create a league </app-default-button>
            </p>
            <small v-if="isAnonymous">
              Already have a league?
              <router-link to="/login">Log in</router-link>
            </small>
            <!-- @*@Html.Partial("CflNews", Model.News)*@ -->
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <archive-leagues v-if="hasArchiveLeagues" :archiveLeagues="archiveLeagues" />
  </div>
</template>

<style scoped>
.league-heading {
  text-align: center;
}

.matchup {
  border-bottom: 1px solid var(--bg-color-primary);
}
</style>

<script>
import { firestore } from "../modules/firebase"
import MatchupPreview from "../components/league/MatchupPreview.vue"
import AppPrimaryButton from "../components/buttons/AppPrimaryButton.vue"
import AppDefaultButton from "../components/buttons/AppDefaultButton.vue"
import Scoreboard from "../components/common/Scoreboard.vue"
import ArchiveLeagues from "./league/ArchiveLeagues.vue"
import FocusGame from "../components/common/FocusGame.vue"

export default {
  name: "home",
  components: {
    MatchupPreview,
    AppPrimaryButton,
    AppDefaultButton,
    Scoreboard,
    ArchiveLeagues,
    FocusGame,
  },
  data() {
    return {
      leagues: [],
      archiveLeagues: [],
      leaguesUnsubscribe: null,
    }
  },
  computed: {
    hasLeagues() {
      return this.leagues && this.leagues.length > 0
    },
    hasArchiveLeagues() {
      return this.archiveLeagues && this.archiveLeagues.length > 0
    },
    isAnonymous() {
      return this.$store.state.isAnonymous
    },
    uid() {
      return this.$store.state.uid
    },
    randomSlogan() {
      let slogans = [
        "Fantasy football, eh?",
        "Long live the rouge",
        "Snow football is good football",
        "12 > 11",
        "3 > 4",
      ]
      return slogans[Math.floor(Math.random() * slogans.length)]
    },
    weekNumber() {
      return this.$root.state.current_week
    },
  },
  methods: {
    bind(uid) {
      let leaguesRef = firestore.collection("user").doc(uid).collection("league").orderBy("joined")
      this.$bind("leagues", leaguesRef)

      let archivesRef = firestore.collection("user").doc(uid).collection("archive_league").orderBy("joined")
      this.$bind("archiveLeagues", archivesRef)
    },
    unbind(uid) {
      try {
        this.$unbind("leagues")
      } catch (err) {
        // it's fine, probably haven't logged in yet
      }
    },
  },
  watch: {
    uid: {
      immediate: true,
      handler(uid) {
        if (uid != null) {
          this.bind(uid)
        } else {
          this.unbind()
        }
      },
    },
  },
}
</script>
