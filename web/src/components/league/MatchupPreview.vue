<template>
  <v-container v-if="matchup">
    <v-row v-if="matchup.type == 'loser'">
      <v-col cols="12" class="text-center"> Loser Game </v-col>
    </v-row>
    <v-row>
      <v-col cols="5">
        <div v-if="matchup.away" class="roster-name">
          <router-link
            :to="{
              name: 'roster',
              params: { leagueId: leagueId, rosterId: matchup.away.id },
            }"
            :class="matchupStateClass(awayScore, homeScore)"
            >{{ matchup.away.name }}</router-link
          >
          <!-- <div class="record caption">{{ matchup.away.record }}</div> -->
        </div>
        <div v-if="!matchup.away">{{ noAwayTeamText }}</div>
      </v-col>
      <v-col cols="2">
        <v-spacer />
      </v-col>

      <v-col cols="5" class="text-right">
        <div v-if="matchup.home" class="roster-name">
          <router-link
            :to="{
              name: 'roster',
              params: { leagueId: leagueId, rosterId: matchup.home.id },
            }"
            :class="matchupStateClass(homeScore, awayScore)"
          >
            {{ matchup.home.name }}</router-link
          >
          <!-- <div class="record caption">{{ matchup.home.record }}</div> -->
        </div>
        <p v-if="!matchup.home">TBD</p>
      </v-col>

      <v-col cols="5" class="pt-0">
        <span v-if="awayScore != null && !isBye" :class="matchupStateClass(awayScore, homeScore)">
          <score :score="awayScore" />
        </span>
      </v-col>

      <v-col cols="2" class="pt-0 text-center">
        <router-link
          v-if="matchupId && !isBye"
          :to="{
            name: 'matchup',
            params: {
              leagueId: leagueId,
              weekNumber: weekNumber,
              matchupId: matchupId,
            },
          }"
          >vs
        </router-link>
      </v-col>

      <v-col cols="5" class="pt-0 text-right">
        <span v-if="homeScore != null" :class="matchupStateClass(homeScore, awayScore)">
          <score :score="homeScore" />
        </span>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.roster-name {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.matchup td.roster {
  width: 35%;
}

.matchup td.score {
  width: 10%;
}

.matchup td {
  border-top: 1px solid var(--bg-color-secondary);
}
.roster-away {
  text-align: left;
}
.score-away {
  text-align: right;
  vertical-align: middle;
  padding-right: 1em;
  border-right: 1px solid var(--bg-color-secondary);
}
.roster-home {
  text-align: right;
}
.score-home {
  padding-left: 1em;
  vertical-align: middle;
  border-left: 1px solid var(--bg-color-secondary);
}
.record {
  font-size: small;
}
td.vs {
  vertical-align: middle;
  padding-left: 1em;
  padding-right: 1em;
}
</style>

<script>
import scoreboard from "../../mixins/scoreboard"
import { firestore } from "../../modules/firebase"
import * as formatter from "../../modules/formatter"
import { calculateMultiple, getRosterScoreRef } from "../../modules/scoring"
import Score from "../Score.vue"

export default {
  components: { Score },
  name: "matchup-preview",
  mixins: [scoreboard],
  props: {
    matchup: Object,
    leagueId: String,
    weekNumber: Number,
  },

  data() {
    return {
      away: null,
      home: null,
      awayPlayers: null,
      homePlayers: null,
      scoringSettings: null,
    }
  },

  computed: {
    season() {
      return this.$root.currentSeason
    },

    matchupType() {
      return this.matchup.type
    },

    isBye() {
      return this.matchup.type == "playoff_bye"
    },

    noAwayTeamText() {
      if (this.isBye) return "Bye"

      return "TBD"
    },

    matchupId() {
      return this.matchup.id || this.matchup.matchup_id
    },

    isCurrentWeek() {
      return this.weekNumber == this.$root.state.current_week
    },

    awayScore() {
      return this.awayPlayers && this.scoringSettings ? calculateMultiple(this.scoringSettings, this.awayPlayers) : 0
    },

    homeScore() {
      return this.homePlayers && this.scoringSettings ? calculateMultiple(this.scoringSettings, this.homePlayers) : 0
    },
  },
  methods: {
    formatScore(score) {
      if (score == null || score == undefined) score = 0
      return formatter.formatScore(score)
    },
    matchupStateClass(scoreFor, scoreAgainst) {
      return scoreFor > scoreAgainst ? "winning" : ""
    },
    viewMatchup() {
      this.$router.push({
        name: "matchup",
        params: { leagueId, matchupId: matchup.id },
      })
    },
  },

  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        if (leagueId) {
          let path = `league/${leagueId}/config/scoring`
          let ref = firestore.doc(path)
          this.$bind("scoringSettings", ref)
        }
      },
    },

    matchup: {
      immediate: true,
      handler(matchup) {
        if (matchup) {
          if (matchup.away) {
            let path = `league/${this.leagueId}/roster/${matchup.away.id}`
            let ref = firestore.doc(path)
            this.$bind("away", ref)
          }

          if (matchup.home) {
            let path = `league/${this.leagueId}/roster/${matchup.home.id}`
            let ref = firestore.doc(path)
            this.$bind("home", ref)
          }
        }
      },
    },
    away: {
      immediate: true,
      async handler(away) {
        if (away) {
          this.$bind("awayPlayers", getRosterScoreRef(this.season, this.weekNumber, away))
        }
      },
    },

    home: {
      immediate: true,
      async handler(home) {
        if (home) {
          this.$bind("homePlayers", getRosterScoreRef(this.season, this.weekNumber, home))
        }
      },
    },
  },
}
</script>
