<template>
  <div v-if="player">
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <div class="team-colors" :class="player.team.abbreviation">{{ player.uniform }}</div>
            {{ player.display_name }}
          </v-card-title>
          <v-card-subtitle>
            <span>{{ player.position.toUpperCase() }}</span>
            <span> - </span>
            <span>{{ player.team.location }} {{ player.team.name }}</span>
            <div v-if="statusText" :class="statusClass">{{ statusText }}</div>
          </v-card-subtitle>

          <v-card-subtitle>
            <div v-if="scores"><label>Fantasy Rank:</label> {{ scores.rank }}</div>
            <!-- Owner -->
            <!-- Add -->
          </v-card-subtitle>

          <v-card-subtitle>
            <div v-if="hasHeight && hasWeight"><label>Height/Weight:</label> {{ height }} / {{ weight }}</div>
            <div v-if="hasHeight && !hasWeight"><label>Height:</label> {{ height }}</div>
            <div v-if="!hasHeight && hasWeight"><label>Weight:</label> {{ weight }}</div>
            <div v-if="hometown"><label>Hometown:</label> {{ hometown }}</div>
            <div v-if="college"><label>College:</label> {{ college }}</div>
          </v-card-subtitle>

          <v-card-text>
            <a :href="cflLink" target="_blank">CFL Page</a>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <h4>Game Log</h4>
        <v-simple-table v-if="gameLog">
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
              <template v-for="log in gameLog">
                <tr :key="'stats' + log.id">
                  <!-- <game-date :game="log.game" /> -->
                  <game-result v-if="log.game" :game="log.game" :player="player" />
                  <td class="text-no-wrap">
                    <span>{{ formatScore(log.score ? log.score.total_score : 0) }}</span>
                    <v-icon @click="detailedLog = log" v-if="!detailedLog" small color="grey" class="mt-n1 pl-1"
                      >mdi-help-circle</v-icon
                    >
                    <v-icon
                      @click="detailedLog = null"
                      v-if="detailedLog && detailedLog.id == log.id"
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

                <tr v-if="detailedLog && detailedLog.id == log.id" :key="'scoring' + log.id">
                  <td>Score details:</td>
                  <td>
                    <span>{{ formatScore(log.score ? log.score.total_score : 0) }}</span>
                  </td>

                  <template v-if="showPassing">
                    <game-value :value="log.score.pass_attempts" />
                    <game-value :value="log.score.pass_completions" />
                    <game-value :value="log.score.pass_net_yards" />
                    <td></td>
                    <game-value :value="log.score.pass_touchdowns" />
                    <game-value :value="log.score.pass_interceptions" />
                  </template>

                  <template v-if="showRushing && showRushingFirst">
                    <game-value :value="log.score.rush_attempts" />
                    <game-value :value="log.score.rush_net_yards" />
                    <game-value :value="log.score.rush_touchdowns" />
                    <game-average :attempts="log.score.rush_attempts" :yards="log.score.rush_net_yards" />
                    <td></td>
                  </template>

                  <template v-if="showReceiving">
                    <game-value :value="log.score.receive_caught" />
                    <game-value :value="log.score.receive_attempts" />
                    <game-value :value="log.score.receive_yards" />
                    <game-value :value="log.score.receive_touchdowns" />
                    <td></td>
                    <td></td>
                  </template>

                  <template v-if="showFumbles">
                    <game-value :value="getFumbleScore(log.score)" />
                  </template>

                  <template v-if="showConvert2">
                    <game-value :value="log.score.two_point_converts_made" />
                  </template>

                  <template v-if="showRushing && !showRushingFirst">
                    <game-value :value="log.score.rush_attempts" />
                    <game-value :value="log.score.rush_net_yards" />
                    <game-value :value="log.score.rush_touchdowns" />
                    <game-average :attempts="log.score.rush_attempts" :yards="log.score.rush_net_yards" />
                    <td></td>
                  </template>

                  <template v-if="showDefence">
                    <td></td>
                    <game-value :value="log.score.tackles_defensive" />
                    <game-value :value="log.score.tackles_special_teams" />
                    <game-value :value="log.score.sacks_qb_made" />
                    <game-value :value="log.score.interceptions" />
                    <game-value :value="log.score.fumbles_forced" />
                    <game-value :value="log.score.fumbles_recovered" />
                  </template>

                  <template v-if="showReturning">
                    <game-value :value="log.score.field_goal_returns_yards" />
                    <game-value :value="log.score.field_goal_returns_touchdowns" />
                    <game-value :value="log.score.kick_returns_yards" />
                    <game-value :value="log.score.kick_returns_touchdowns" />
                    <game-value :value="log.score.punt_returns_yards" />
                    <game-value :value="log.score.punt_returns_touchdowns" />
                  </template>

                  <template v-if="showKicking">
                    <game-value :value="log.score.field_goal_attempts" />
                    <game-value :value="log.score.field_goal_made" />
                    <game-value :value="log.score.field_goal_misses" />
                    <game-percent :attempts="log.score.field_goal_attempts" :successes="log.score.field_goal_made" />
                    <game-value :value="log.score.one_point_converts_made" />
                    <game-value :value="getSingleScore(log.score)" />
                  </template>
                </tr>
              </template>
            </tbody>
          </template>
        </v-simple-table>
      </v-col>
    </v-row>
  </div>
</template>

<style scoped>
label {
  font-weight: bold;
}
</style>

<script>
import { playerStatus, positionType } from "../../api/110yards/constants"
import GameAverage from "../../components/player/stats/GameAverage.vue"
import GamePercent from "../../components/player/stats/GamePercent.vue"
import GameResult from "../../components/player/stats/GameResult.vue"
import GameValue from "../../components/player/stats/GameValue.vue"
import games from "../../mixins/games"
import { firestore } from "../../modules/firebase"
import * as formatter from "../../modules/formatter"

export default {
  name: "PlayerDetails",
  components: {
    GameAverage,
    GameResult,
    GamePercent,
    GameValue,
  },
  mixins: [games],
  props: {
    leagueId: { type: String, required: true },
    playerId: { type: String, required: true },
  },

  data() {
    return {
      player: null,
      scores: null,
      detailedLog: null,
      owner: null,
    }
  },

  computed: {
    season() {
      // TODO: 2022 - state
      return process.env.VUE_APP_SEASON
    },

    gameLog() {
      if (!this.player || !this.player.game_stats || !this.scores || !this.gamesById) return []

      let log = []
      for (let gameId in this.player.game_stats) {
        log.push({
          id: gameId,
          game: this.getGame(gameId),
          stats: this.player.game_stats[gameId],
          score: this.getGameScore(gameId),
        })
      }

      return log
    },

    statusClass() {
      return this.player && this.player.status_current == playerStatus.Active ? "" : "red--text"
    },

    statusText() {
      return this.player ? playerStatus.getFullText(this.player.status_current) : null
    },

    cflLink() {
      return `https://www.cfl.ca/players/player/${this.player.id}`
    },

    hasHeight() {
      return this.player && this.player.height
    },

    hasWeight() {
      return this.player && this.player.weight
    },

    height() {
      if (!this.hasHeight) return
      let height = this.player.height

      if (!height) return

      let ft = parseInt(height)
      let inches = parseInt(height.split(".")[1])

      return `${ft}'${inches}"`
    },

    weight() {
      if (!this.hasWeight) return

      return `${this.player.weight} lbs`
    },

    hometown() {
      if (!this.player) return

      let country = this.player.birth_country_name
      let prov = this.player.birth_state_abbreviation
      let city = this.player.birth_city

      if (!city) return

      if (country == "Canada" && prov) return `${city}, ${prov}`
      if (country == "United States" && prov) return `${city}, ${prov}`
      if (country) return `${city}, ${country}`

      return city
    },

    college() {
      return this.player && this.player.college_fullName ? this.player.college_fullName : null
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
      return this.hasStatKey("")
    },

    showFumbles() {
      return this.hasStatKey("receive_fumbles") || this.hasStatKey("pass_fumbles")
    },

    showReturning() {
      return this.hasStatKey("kick_returns") || this.hasStatKey("punt_returns") || this.hasStatKey("field_goal_returns")
    },
  },

  methods: {
    formatScore(score) {
      if (score == null || score == undefined) return formatter.formatScore(0)
      return formatter.formatScore(score)
    },
    hasStatKey(key) {
      if (this.scores && this.scores.game_scores) {
        let gameIds = Object.keys(this.scores.game_scores)
        let lastGameId = gameIds[gameIds.length - 1]
        let inLastGameStats = key in this.scores.game_stats[lastGameId]
        if (inLastGameStats) return true
      }

      if (!this.scores || !this.scores.season_stats) return false
      let inSeasonStats = key in this.scores.season_stats && this.scores.season_stats[key] != 0

      if (inSeasonStats) return true
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

    configureReferences() {
      if (!this.leagueId || !this.playerId) return

      let playerRef = firestore.doc(`season/${this.season}/player/${this.playerId}`)
      this.$bind("player", playerRef)

      let scoresRef = firestore.doc(`league/${this.leagueId}/player_score/${this.playerId}`)
      this.$bind("scores", scoresRef)
    },
  },

  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        if (!leagueId) return
        this.configureReferences()
      },
    },

    playerId: {
      immediate: true,
      handler(playerId) {
        if (!playerId) return
        this.configureReferences()
      },
    },
  },
}
</script>
