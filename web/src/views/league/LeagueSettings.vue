<template>
  <div v-if="league && scoringInfo">
    <league-menu :league="league" />
    <v-card class="mt-4">
      <v-card-title>Scoring settings</v-card-title>
      <v-card-text>
        <v-simple-table>
          <template v-slot:default>
            <template v-for="(section, index) in scoringInfo.sections">
              <thead :key="'header-' + index">
                <tr>
                  <th colspan="1">{{ section.description }}</th>
                  <th>Value</th>
                  <th></th>
                </tr>
              </thead>
              <tbody :key="index">
                <tr v-for="action in section.actions" :key="action.id">
                  <td class="action">{{ action.description }}</td>
                  <td class="value">
                    <app-form-label>{{ scoringConfig[action.id] }}</app-form-label>
                  </td>
                  <td>
                    <span v-if="action.show_yards_per_point">
                      {{ calculateYardsPerPoint(scoringConfig[action.id]) }}
                    </span>
                  </td>
                </tr>
                <tr>
                  <td colspan="3">
                    <!-- spacer -->
                  </td>
                </tr>
              </tbody>
            </template>
          </template>
        </v-simple-table>
      </v-card-text>
    </v-card>
    <v-card class="mt-5">
      <v-card-text></v-card-text>
    </v-card>
  </div>
</template>

<script>
import AppFormLabel from "../../components/inputs/AppFormLabel.vue"
import LeagueMenu from "../../components/league/LeagueMenu.vue"
import { firestore } from "../../modules/firebase"

export default {
  name: "LeagueSettings",

  components: { LeagueMenu, AppFormLabel },
  props: {
    leagueId: { type: String, required: true },
  },

  data() {
    return {
      league: null,
      scoringConfig: null,
      scoringInfo: null,
    }
  },

  methods: {
    calculateYardsPerPoint(value) {
      let numericValue = parseFloat(value)
      if (numericValue == 0 || isNaN(numericValue)) {
        return ""
      }

      let yardsPerPoint = 1 / numericValue

      return `${yardsPerPoint} yards = 1 point`
    },

    configureBindings() {
      let leagueRef = firestore.doc(`league/${this.leagueId}`)
      this.$bind("league", leagueRef)

      let configRef = leagueRef.collection("/config")

      let scoringConfigRef = configRef.doc("scoring")

      this.$bind("scoringConfig", scoringConfigRef)

      this.$bind("scoringInfo", firestore.doc("public/scoring_info"))
    },
  },

  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        if (leagueId) {
          this.configureBindings()
        }
      },
    },
  },
}
</script>
