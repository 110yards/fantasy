<template>
  <v-row v-if="leagueId && weekNumber" class="heading mb-2 text-right">
    <v-col cols="5" class="roster-name pl-4">
      <!-- <team-header
          :leagueId="leagueId"
          :roster="awayRoster"
          :opponent="homeRoster"
          :reverse="true"
          :enableProjections="enableProjections"
          :isCurrentWeek="isCurrentWeek"
          :projection="awayProjection"
          :weekNumber="weekNumber"
        /> -->
      <v-row>
        <v-col class="pb-0 caption roster-name" :class="teamClass">
          <span v-if="away">
            <router-link :to="{ name: 'roster', params: { leagueId: leagueId, rosterId: away.id } }">
              {{ away.name }}
            </router-link>
          </span>
          <span v-else>TBD</span>
        </v-col>
      </v-row>

      <v-row>
        <v-col class="py-0 text-h4" :class="scoreClass">
          <score :score="awayScore" />
        </v-col>
      </v-row>

      <v-row>
        <v-col class="py-0 grey--text">
          <!-- <score v-if="enableProjections" :score="projection" /> -->
        </v-col>
      </v-row>

      <v-row v-if="showMatchupProgress">
        <v-col>
          <matchup-progress :roster="home" :reverse="reverse" :leagueId="leagueId" :class="!reverse ? 'pr-1' : ''" />
        </v-col>
      </v-row>
    </v-col>

    <v-col cols="2" class="text-center">
      <v-row>
        <v-col class="pb-0">vs</v-col>
      </v-row>
    </v-col>

    <v-col cols="5" class="roster-name pr-4 text-left">
      <!-- <team-header
        :leagueId="leagueId"
        :roster="homeRoster"
        :opponent="awayRoster"
        :enableProjections="enableProjections"
        :isCurrentWeek="isCurrentWeek"
        :projection="homeProjection"
        :weekNumber="weekNumber"
      /> -->
      <v-row>
        <v-col class="pb-0 caption roster-name" :class="teamClass">
          <span v-if="home">
            <router-link :to="{ name: 'roster', params: { leagueId: leagueId, rosterId: home.id } }">
              {{ home.name }}
            </router-link>
          </span>
          <span v-else>TBD</span>
        </v-col>
      </v-row>

      <v-row>
        <v-col class="py-0 text-h4" :class="scoreClass">
          <score :score="homeScore" />
        </v-col>
      </v-row>

      <v-row>
        <v-col class="py-0 grey--text">
          <!-- <score v-if="enableProjections" :score="projection" /> -->
        </v-col>
      </v-row>

      <v-row v-if="showMatchupProgress">
        <v-col>
          <matchup-progress :roster="home" :reverse="reverse" :leagueId="leagueId" :class="!reverse ? 'pr-1' : ''" />
        </v-col>
      </v-row>
    </v-col>
  </v-row>
</template>

<script>
import { calculateMultiple, getRosterScoreRef } from "../../../modules/scoring"
import Score from "../../Score.vue"

export default {
  components: { Score },

  props: {
    away: { type: Object, required: false },
    home: { type: Object, required: false },
    weekNumber: { required: true },
  },

  data() {
    return {
      awayPlayers: null,
      homePlayers: null,
    }
  },

  computed: {
    season() {
      return this.$root.currentSeason
    },

    leagueId() {
      return this.$root.leagueId
    },

    awayScore() {
      // TODO: roster score does not update as player scores update.  Need a way to trigger a firebase refresh.
      return this.awayPlayers ? calculateMultiple(this.$root.leagueScoringSettings, this.awayPlayers) : 0
    },

    homeScore() {
      return this.homePlayers ? calculateMultiple(this.$root.leagueScoringSettings, this.homePlayers) : 0
    },

    showMatchupProgress() {
      return false // TODO
    },

    enableProjections() {
      return false //  TODO
    },
  },

  methods: {
    setupScoreRef() {},
  },

  watch: {
    away: {
      immediate: true,
      handler(away) {
        if (away) this.$bind("awayPlayers", getRosterScoreRef(this.season, this.weekNumber, away))
      },
    },

    home: {
      immediate: true,
      handler(home) {
        if (home) this.$bind("homePlayers", getRosterScoreRef(this.season, this.weekNumber, home))
      },
    },
  },
}
</script>
