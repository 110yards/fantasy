<template>
  <v-container v-if="league" :class="mobile ? 'mobile' : ''">
    <v-row v-for="position in positions" :key="position.id" class="position-row">
      <v-col cols="12 px-0">
        <v-row>
          <v-col cols="4" class="trim pl-4">
            <v-row>
              <v-col class="pb-0">
                <player-link
                  :player="getPlayer(position.id, away)"
                  :leagueId="league.id"
                  :shortenName="mobile"
                  :showTeamLogo="!mobile"
                  :showPosition="!mobile"
                  :showStatus="!mobile"
                  :showShortPlayerStatus="mobile"
                  :showNational="!mobile"
                  :maxNameLength="mobile ? 10 : null"
                />
              </v-col>
            </v-row>
            <v-row v-if="mobile" class="">
              <v-col class="mt-n2 pb-0 grey--text caption">
                <span v-if="getPlayer(position.id, away)">
                  <span>{{ getPlayer(position.id, away).team.abbr }}</span>
                  <span>&nbsp;- {{ getPlayer(position.id, away).position.toUpperCase() }}</span>
                  <national-status
                    v-if="getPlayer(position.id, away)"
                    :national_status="getPlayer(position.id, away).national_status"
                  />
                </span>
              </v-col>
            </v-row>
            <v-row class="">
              <v-col class="mt-n3 pb-0 grey--text caption">
                <game-state
                  v-if="scoreboard"
                  :player="getPlayer(position.id, away)"
                  :short="mobile"
                  :scoreboard="scoreboard"
                />
              </v-col>
            </v-row>
          </v-col>

          <v-col cols="1" class="px-0">
            <v-row>
              <v-col class="pb-0 text-right">
                <position-score
                  :position="getPosition(position.id, away)"
                  :leagueId="league.id"
                  :weekNumber="weekNumber"
                  :scoreboard="scoreboard"
                />
              </v-col>
            </v-row>

            <v-row class="caption grey--text">
              <v-col class="pt-1 text-right">
                <player-projection
                  v-if="enableProjections"
                  :leagueId="league.id"
                  :player="getPlayer(position.id, away)"
                />
              </v-col>
            </v-row>
          </v-col>

          <v-col cols="2" class="text-center grey--text px-0">{{ getPositionName(position) }}</v-col>

          <v-col cols="1" class="px-0">
            <v-row>
              <v-col class="pb-0 text-left">
                <position-score
                  :position="getPosition(position.id, home)"
                  :leagueId="league.id"
                  :weekNumber="weekNumber"
                  :scoreboard="scoreboard"
                />
              </v-col>
            </v-row>

            <v-row class="caption grey--text">
              <v-col class="pt-1 text-left">
                <player-projection
                  v-if="enableProjections"
                  :leagueId="league.id"
                  :player="getPlayer(position.id, home)"
                />
              </v-col>
            </v-row>
          </v-col>

          <v-col cols="4" class="pl-0 pr-4">
            <v-row>
              <v-col class="pb-0 text-right">
                <player-link
                  :player="getPlayer(position.id, home)"
                  :leagueId="league.id"
                  :shortenName="mobile"
                  :showTeamLogo="!mobile"
                  :showPosition="!mobile"
                  :showStatus="!mobile"
                  :showShortPlayerStatus="mobile"
                  :showNational="!mobile"
                  :maxNameLength="mobile ? 10 : null"
                  :reverse="true"
                />
              </v-col>
            </v-row>
            <v-row v-if="mobile" class="">
              <v-col class="mt-n2 pb-0 grey--text caption text-right">
                <span v-if="getPlayer(position.id, home)">
                  <national-status
                    v-if="getPlayer(position.id, home)"
                    :national_status="getPlayer(position.id, home).national_status"
                  />
                  <span>{{ getPlayer(position.id, home).team.abbr }}</span>
                  <span>&nbsp;- {{ getPlayer(position.id, home).position.toUpperCase() }}</span>
                </span>
              </v-col>
            </v-row>
            <v-row class="">
              <v-col class="mt-n3 pb-0 grey--text caption text-right">
                <game-state
                  v-if="scoreboard"
                  :player="getPlayer(position.id, home)"
                  :short="mobile"
                  :scoreboard="scoreboard"
                />
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
#total {
  border-top: 1px solid var(--bg-color-primary);
}

.mobile .position-row {
  line-height: 0.75em;
  font-size: 0.9em;
  padding-bottom: 1em;
}
</style>

<script>
import GameState from "../GameState.vue"
import PlayerLink from "../../player/PlayerLink.vue"
import * as formatter from "../../../modules/formatter"
import PlayerProjection from "../PlayerProjection.vue"
import NationalStatus from "../../player/NationalStatus.vue"
import { positionType } from "../../../api/110yards/constants"
import PositionScore from "../PositionScore.vue"
import scoreboard from "../../../mixins/scoreboard"

export default {
  components: { PlayerLink, GameState, PlayerProjection, NationalStatus, PositionScore },
  mixins: [scoreboard],
  name: "MatchupVs",
  props: {
    league: {
      type: Object,
      required: true,
    },
    weekNumber: {
      required: true,
    },
    away: {
      type: Object,
      required: false,
    },
    home: {
      type: Object,
      required: false,
    },
    mobile: { type: Boolean, required: false, default: false },
    enableProjections: { type: Boolean, required: false, default: false },
  },

  computed: {
    positions() {
      if (!this.league) return []

      let positions = Object.values(this.league.positions)
      return positions.filter(spot => this.$root.isActivePositionType(spot.position_type))
    },
  },

  methods: {
    getPosition(positionId, roster) {
      if (!roster) return null

      let position = Object.values(roster.positions).filter(p => p.id == positionId)
      return position.length > 0 ? position[0] : null
    },

    getPlayer(positionId, roster) {
      let position = this.getPosition(positionId, roster)

      return position != null ? position.player : null
    },

    getPlayerScore(positionId, roster) {
      let position = this.getPosition(positionId, roster)

      return this.formatScore(position != null ? position.game_score : 0.0)
    },

    formatScore(score) {
      if (score == null || score == undefined) score = 0

      return formatter.formatScore(score)
    },

    getPositionName(position) {
      return positionType.spotName(position.position_type)
    },
  },
}
</script>
