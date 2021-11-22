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
          {{ formatScore(awayScore) }}
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
          {{ formatScore(homeScore) }}
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
import { rosterScore } from "../../api/110yards/score"
import scoreboard from "../../mixins/scoreboard"
import * as formatter from "../../modules/formatter"

export default {
  name: "matchup-preview",
  mixins: [scoreboard],
  props: {
    matchup: Object,
    leagueId: String,
    weekNumber: Number,
  },

  data() {
    return {
      awayScore: null,
      homeScore: null,
    }
  },

  computed: {
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

    awayRoster() {
      return this.matchup != null ? this.matchup.away : null
    },

    homeRoster() {
      return this.matchup != null ? this.matchup.home : null
    },
    isCurrentWeek() {
      return this.weekNumber == this.$root.state.current_week
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

    async updateAwayScore() {
      if (this.awayRoster && this.isCurrentWeek && this.scoreboard) {
        let awayInfo = await rosterScore(this.leagueId, this.awayRoster.id)
        this.awayScore = awayInfo.score
      } else {
        this.awayScore = this.matchup.away_score
      }
    },

    async updateHomeScore() {
      if (this.homeRoster && this.isCurrentWeek && this.scoreboard) {
        let homeInfo = await rosterScore(this.leagueId, this.homeRoster.id)
        this.homeScore = homeInfo.score
      } else {
        this.homeScore = this.matchup.home_score
      }
    },
  },

  watch: {
    awayRoster: {
      immediate: true,
      async handler(awayRoster) {
        this.updateAwayScore()
      },
    },

    homeRoster: {
      immediate: true,
      async handler(homeRoster) {
        this.updateHomeScore()
      },
    },

    scoreboard: {
      async handler(scoreboard) {
        this.updateAwayScore()
        this.updateHomeScore()
      },
    },
  },
}
</script>
