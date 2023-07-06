<template>
  <div>
    <div v-if="player">
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title>
              <div class="team-colors" :class="player.team_abbr">
                {{ player.uniform || "-" }}
              </div>
              {{ player.full_name }}
              <canadian-status :isCanadian="player.canadian_player" />
            </v-card-title>
            <v-card-subtitle>
              <span>{{ player.position.toUpperCase() }}</span>
              <span> - </span>
              <span>{{ teamName }}</span>
              <div v-if="statusText" :class="statusClass">{{ statusText }}</div>
            </v-card-subtitle>

            <v-card-subtitle>
              <div><label>Rank: </label> {{ rank }}</div>
              <div><label>Score: </label> <score :score="playerScore.total_score" /></div>
              <div>
                <label>Owner: </label>
                <league-roster-link v-if="isOwned" :leagueId="leagueId" :roster="ownerRoster" :trim="false" />
                <span v-else>Free agent</span>
              </div>
              <!-- Add -->
            </v-card-subtitle>

            <v-card-subtitle>
              <div v-if="player.age"><label>Age:</label> {{ player.age }}</div>
              <div v-if="hasHeight && hasWeight">
                <label>Height/Weight:</label> {{ player.height }} /
                {{ player.weight }}
              </div>
              <div v-if="hasHeight && !hasWeight"><label>Height:</label> {{ player.height }}</div>
              <div v-if="!hasHeight && hasWeight"><label>Weight:</label> {{ player.weight }}</div>
              <div v-if="player.birth_place"><label>Hometown:</label> {{ player.birth_place }}</div>
              <div v-if="player.school"><label>College:</label> {{ player.school }}</div>
            </v-card-subtitle>

            <!-- <v-card-text>
              <a :href="player.cfl_url" target="_blank">CFL Page</a>
            </v-card-text> -->
          </v-card>
        </v-col>
      </v-row>

      <v-row v-if="playerSeason">
        <v-col cols="12">
          <h4>Game Log</h4>
          <v-simple-table v-if="playerSeason.games">
            <template>
              <thead>
                <tr>
                  <th colspan="2"></th>
                  <th v-if="showPassing" colspan="6">Passing</th>
                  <th v-if="showRushing" colspan="5">Rushing</th>
                  <th v-if="showReceiving" colspan="6">Receiving</th>
                  <th v-if="showFumbles"></th>
                  <th v-if="showConvert2"></th>
                  <th v-if="showDefence" colspan="7">Defense</th>
                  <th v-if="showReturning" colspan="7">Kick Returns</th>
                  <th v-if="showKicking" colspan="7">Kicking</th>
                </tr>
                <tr>
                  <th colspan="1">Game</th>
                  <th>Score</th>

                  <template v-if="showPassing">
                    <th>Passes</th>
                    <th>Comp</th>
                    <th>Yards</th>
                    <th>Y/A</th>
                    <th>TD</th>
                    <th>Int</th>
                  </template>

                  <template v-if="showRushing && showRushingFirst">
                    <th>Rushes</th>
                    <th>Yards</th>
                    <th>TD</th>
                    <th>Avg</th>
                    <th>Long</th>
                  </template>

                  <template v-if="showReceiving">
                    <th>Rec</th>
                    <th>Att</th>
                    <th>Yards</th>
                    <th>TD</th>
                    <th>Avg</th>
                    <th>Long</th>
                  </template>

                  <template v-if="showRushing && !showRushingFirst">
                    <th>Rushes</th>
                    <th>Yards</th>
                    <th>TD</th>
                    <th>Avg</th>
                    <th>Long</th>
                  </template>

                  <template v-if="showFumbles">
                    <th>Fum</th>
                  </template>

                  <template v-if="showConvert2">
                    <th>2PT</th>
                  </template>

                  <template v-if="showDefence">
                    <th>TT</th>
                    <th>DT</th>
                    <th>ST</th>
                    <th>QS</th>
                    <th>INT</th>
                    <th>FF</th>
                    <th>FR</th>
                  </template>

                  <template v-if="showReturning">
                    <th>FG Yd</th>
                    <th>FG TD</th>
                    <th>KR Yd</th>
                    <th>KR TD</th>
                    <th>PR Yd</th>
                    <th>PR TD</th>
                  </template>

                  <template v-if="showKicking">
                    <th>FGA</th>
                    <th>Make</th>
                    <th>Miss</th>
                    <th>%</th>
                    <th>1PT</th>
                    <th>Sgl</th>
                  </template>
                </tr>
              </thead>

              <tbody>
                <template v-for="log in playerSeason.games">
                  <tr :key="log.game_id">
                    <!-- <game-date :game="log.game" /> -->
                    <game-result :gameResult="log.game_result" />
                    <td class="text-no-wrap">
                      <score :score="calculateGameScore(log.stats)" />
                      <v-icon @click="detailedLog = log" v-if="!detailedLog" small color="grey" class="mt-n1 pl-1"
                        >mdi-help-circle</v-icon
                      >
                      <v-icon
                        @click="detailedLog = null"
                        v-if="detailedLog && detailedLog.game_id == log.game_id"
                        small
                        color="grey"
                        class="mt-n1 pl-1"
                        >mdi-close</v-icon
                      >
                    </td>

                    <template v-if="showPassing">
                      <game-value :value="log.stats.pass_attempts" />
                      <game-value :value="log.stats.pass_completions" />
                      <game-value :value="log.stats.pass_net_yards" />
                      <game-average :attempts="log.stats.pass_completions" :yards="log.stats.pass_net_yards" />
                      <game-value :value="log.stats.pass_touchdowns" />
                      <game-value :value="log.stats.pass_interceptions" />
                    </template>

                    <template v-if="showRushing && showRushingFirst">
                      <game-value :value="log.stats.rush_attempts" />
                      <game-value :value="log.stats.rush_net_yards" />
                      <game-value :value="log.stats.rush_touchdowns" />
                      <game-average :attempts="log.stats.rush_attempts" :yards="log.stats.rush_net_yards" />
                      <game-value :value="log.stats.rush_long" />
                    </template>

                    <template v-if="showReceiving">
                      <game-value :value="log.stats.receive_caught" />
                      <game-value :value="log.stats.receive_attempts" />
                      <game-value :value="log.stats.receive_yards" />
                      <game-value :value="log.stats.receive_touchdowns" />
                      <game-average :attempts="log.stats.receive_attempts" :yards="log.stats.receive_yards" />
                      <game-value :value="log.stats.receive_long" />
                    </template>

                    <template v-if="showFumbles">
                      <game-value :value="getFumbleCount(log.stats)" />
                    </template>

                    <template v-if="showConvert2">
                      <game-value :value="log.stats.two_point_converts_made" />
                    </template>

                    <template v-if="showRushing && !showRushingFirst">
                      <game-value :value="log.stats.rush_attempts" />
                      <game-value :value="log.stats.rush_net_yards" />
                      <game-value :value="log.stats.rush_touchdowns" />
                      <game-average :attempts="log.stats.rush_attempts" :yards="log.stats.rush_net_yards" />
                      <game-value :value="log.stats.rush_long" />
                    </template>

                    <template v-if="showDefence">
                      <game-value :value="log.stats.tackles_total" />
                      <game-value :value="log.stats.tackles_defensive" />
                      <game-value :value="log.stats.tackles_special_teams" />
                      <game-value :value="log.stats.sacks_qb_made" />
                      <game-value :value="log.stats.interceptions" />
                      <game-value :value="log.stats.fumbles_forced" />
                      <game-value :value="log.stats.fumbles_recovered" />
                    </template>

                    <template v-if="showReturning">
                      <game-value :value="log.stats.field_goal_returns_yards" />
                      <game-value :value="log.stats.field_goal_returns_touchdowns" />
                      <game-value :value="log.stats.kick_returns_yards" />
                      <game-value :value="log.stats.kick_returns_touchdowns" />
                      <game-value :value="log.stats.punt_returns_yards" />
                      <game-value :value="log.stats.punt_returns_touchdowns" />
                    </template>

                    <template v-if="showKicking">
                      <game-value :value="log.stats.field_goal_attempts" />
                      <game-value :value="log.stats.field_goal_made" />
                      <game-value :value="log.stats.field_goal_misses" />
                      <game-percent :attempts="log.stats.field_goal_attempts" :successes="log.stats.field_goal_made" />
                      <game-value :value="log.stats.one_point_converts_made" />
                      <game-value :value="getSingleCount(log.stats)" />
                    </template>
                  </tr>

                  <tr v-if="detailedLog && detailedLog.game_id == log.game_id" :key="'scoring' + log.game_id">
                    <td>Score details:</td>
                    <td>
                      <score :score="calculateGameScore(detailedLog.stats)" />
                    </td>

                    <template v-if="showPassing">
                      <td><score :score="calculateStatScore(log.stats, 'pass_attempts')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'pass_completions')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'pass_net_yards')" /></td>
                      <td></td>
                      <td><score :score="calculateStatScore(log.stats, 'pass_touchdowns')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'pass_interceptions')" /></td>
                    </template>

                    <template v-if="showRushing && showRushingFirst">
                      <td><score :score="calculateStatScore(log.stats, 'rush_attempts')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'rush_net_yards')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'rush_touchdowns')" /></td>
                      <game-average :attempts="log.score.rush_attempts" :yards="log.score.rush_net_yards" />
                      <td></td>
                    </template>

                    <template v-if="showReceiving">
                      <td><score :score="calculateStatScore(log.stats, 'receive_caught')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'receive_attempts')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'receive_yards')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'receive_touchdowns')" /></td>
                      <td></td>
                      <td></td>
                    </template>

                    <template v-if="showFumbles">
                      <td><score :score="getFumbleScore(log.score)" /></td>
                    </template>

                    <template v-if="showConvert2">
                      <td><score :score="calculateStatScore(log.stats, 'two_point_converts_made')" /></td>
                    </template>

                    <template v-if="showRushing && !showRushingFirst">
                      <td><score :score="calculateStatScore(log.stats, 'rush_attempts')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'rush_net_yards')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'rush_touchdowns')" /></td>
                      <game-average :attempts="log.score.rush_attempts" :yards="log.score.rush_net_yards" />
                      <td></td>
                    </template>

                    <template v-if="showDefence">
                      <td></td>
                      <td><score :score="calculateStatScore(log.stats, 'tackles_defensive')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'tackles_special_teams')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'sacks_qb_made')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'interceptions')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'fumbles_forced')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'fumbles_recovered')" /></td>
                    </template>

                    <template v-if="showReturning">
                      <td><score :score="calculateStatScore(log.stats, 'field_goal_returns_yards')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'field_goal_returns_touchdowns')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'kick_returns_yards')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'kick_returns_touchdowns')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'punt_returns_yards')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'punt_returns_touchdowns')" /></td>
                    </template>

                    <template v-if="showKicking">
                      <td><score :score="calculateStatScore(log.stats, 'field_goal_attempts')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'field_goal_made')" /></td>
                      <td><score :score="calculateStatScore(log.stats, 'field_goal_misses')" /></td>
                      <game-percent :attempts="log.score.field_goal_attempts" :successes="log.score.field_goal_made" />
                      <td><score :score="calculateStatScore(log.stats, 'one_point_converts_made')" /></td>
                      <td><score :score="getSingleScore(log.score)" /></td>
                    </template>
                  </tr>
                </template>
              </tbody>
            </template>
          </v-simple-table>
          <v-card-text v-else>No games</v-card-text>
        </v-col>
      </v-row>
    </div>

    <v-alert type="error" v-if="notFound">Player not found</v-alert>
  </div>
</template>

<style scoped>
label {
  font-weight: bold;
}
</style>

<script>
import { playerStatus, positionType, teams } from "../../api/110yards/constants"
import GameAverage from "../../components/player/stats/GameAverage.vue"
import GamePercent from "../../components/player/stats/GamePercent.vue"
import GameResult from "../../components/player/stats/GameResult.vue"
import GameValue from "../../components/player/stats/GameValue.vue"
import Score from "../../components/Score.vue"
import { firestore } from "../../modules/firebase"
import * as formatter from "../../modules/formatter"
import CanadianStatus from "../../components/player/CanadianStatus.vue"
import { calculate, calculateStat } from "../../modules/scoring"
import LeagueRosterLink from "../../components/league/LeagueRosterLink.vue"

export default {
  name: "PlayerDetails",
  components: {
    GameAverage,
    GameResult,
    GamePercent,
    GameValue,
    CanadianStatus,
    Score,
    LeagueRosterLink,
  },
  props: {
    leagueId: { type: String, required: true },
    playerId: { type: String, required: true },
  },

  data() {
    return {
      player: null,
      playerSeason: null,
      detailedLog: null,
      ownerData: null,
      notFound: false,
      playerScore: null,
      ownerRoster: null,
    }
  },

  computed: {
    isOwned() {
      return this.ownerRoster != null
    },

    rank() {
      return this.playerScore != null ? this.playerScore.rank : "N/A"
    },

    scoring() {
      return this.$root.leagueScoringSettings
    },
    uid() {
      return this.$store.state.uid
    },
    season() {
      return this.$root.state.current_season
    },

    isInjured() {
      return this.player.injury_status != null
    },

    statusClass() {
      return this.player && this.isInjured ? "red--text" : ""
    },

    statusText() {
      if (!this.player || !this.isInjured) {
        return null
      }

      return `${playerStatus.getFullText(this.player.injury_status.status_id)} - ${this.player.injury_status.injury}`
    },

    teamName() {
      return this.player && this.player.team_abbr ? teams.getFullName(this.player.team_abbr) : "Free Agent"
    },

    hasHeight() {
      return this.player.height
    },

    hasWeight() {
      return this.player.weight
    },

    showPassing() {
      return this.hasStatKey("pass_attempts")
    },

    showRushing() {
      return this.hasStatKey("rush_attempts")
    },

    showReceiving() {
      return this.hasStatKey("receive_attempts")
    },

    showRushingFirst() {
      let positions = [positionType.QB, positionType.RB]
      return this.player && positions.includes(this.player.position)
    },

    showKicking() {
      return this.player && this.player.position == positionType.K
    },

    showDefence() {
      return this.hasStatKey("tackles_defensive") || this.hasStatKey("tackles_special_teams")
    },

    showConvert2() {
      return this.hasStatKey("two_point_converts_made")
    },

    showFumbles() {
      return this.hasStatKey("receive_fumbles") || this.hasStatKey("pass_fumbles")
    },

    showReturning() {
      return this.hasStatKey("kick_returns") || this.hasStatKey("punt_returns") || this.hasStatKey("field_goal_returns")
    },
  },

  methods: {
    calculateGameScore(stats) {
      return calculate(this.scoring, stats)
    },
    calculateStatScore(stats, statKey) {
      return calculateStat(this.scoring, stats, statKey)
    },
    formatScore(score) {
      if (score == null || score == undefined) return formatter.formatScore(0)
      return formatter.formatScore(score)
    },
    hasStatKey(key) {
      if (this.playerSeason.stats) {
        return key in this.playerSeason.stats && this.playerSeason.stats[key]
      }

      return false
    },

    getGame(gameId) {
      return this.gamesById[gameId]
    },

    getGameScore(gameId) {
      if (!this.scores) return

      return gameId in this.scores.game_scores ? this.scores.game_scores[gameId] : null
    },

    getSingleCount(stats) {
      let s1 = stats.kicks_singles || 0
      let s2 = stats.punts_singles || 0
      let s3 = stats.field_goal_singles || 0
      return s1 + s2 + s3
    },

    getSingleScore(score) {
      let s1 = score.kicks_singles || 0
      let s2 = score.punts_singles || 0
      let s3 = score.field_goal_singles || 0
      return s1 + s2 + s3
    },

    getFumbleCount(stats) {
      let f1 = stats.receive_fumbles || 0
      let f2 = stats.pass_fumbles || 0
      return f1 + f2
    },

    getFumbleScore(score) {
      let f1 = score.receive_fumbles || 0
      let f2 = score.pass_fumbles || 0
      return f1 + f2
    },
    setupReferences() {
      if (this.playerId && this.season && this.leagueId) {
        let statsRef = firestore.doc(`season/${this.season}/player_season/${this.playerId}`)
        let playerRef = firestore.doc(`players/${this.playerId}`)
        let scoresRef = firestore.doc(`league/${this.leagueId}/player_score/${this.playerId}`)
        let ownerRef = firestore.doc(`league/${this.leagueId}/owned_player/${this.playerId}`)

        this.$bind("playerSeason", statsRef)
        this.$bind("player", playerRef)
        this.$bind("playerScore", scoresRef)
        this.$bind("ownerData", ownerRef)
      }
    },
    setupOwnerReference() {
      if (this.ownerData) {
        let ownerRef = firestore.doc(`league/${this.leagueId}/roster/${this.ownerData.owner_id}`)
        this.$bind("ownerRoster", ownerRef)
      } else {
        this.ownerRoster = null
      }
    },
  },

  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        if (!leagueId) return
        this.setupReferences()
      },
    },

    playerId: {
      immediate: true,
      handler(playerId) {
        if (!playerId) return
        this.setupReferences()
      },
    },

    season: {
      immediate: true,
      handler(season) {
        if (!season) return
        this.setupReferences()
      },
    },

    ownerData: {
      handler(ownerData) {
        this.setupOwnerReference()
      },
    },
  },
}
</script>
