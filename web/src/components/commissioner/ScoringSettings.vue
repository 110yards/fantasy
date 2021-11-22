<template>
  <v-row>
    <v-col cols="12">
      <v-form ref="form" @submit.prevent="submit()">
        <v-simple-table>
          <template v-slot:default>
            <template v-for="(section, index) in scoringInfo.sections">
              <thead :key="'header-' + index">
                <tr>
                  <th colspan="3">{{ section.description }}</th>
                </tr>
              </thead>
              <tbody :key="index">
                <tr v-for="action in section.actions" :key="action.id">
                  <td class="action">{{ action.description }}</td>
                  <td class="value">
                    <app-number-field
                      v-if="!readonly"
                      type="number"
                      v-model="leagueScoring[action.id]"
                      :data-action-id="action.id"
                      :rules="[v => v !== '' || 'Required']"
                    />
                    <app-form-label v-else>{{ leagueScoring[action.id] }}</app-form-label>
                  </td>
                  <td>
                    <span v-if="action.show_yards_per_point">
                      {{ calculateYardsPerPoint(leagueScoring[action.id]) }}
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

        <v-alert v-if="!isWeek1 && leagueStarted && !readonly" type="warning"
          >Changing scoring settings will not affect results for previous weeks</v-alert
        >

        <app-primary-button v-if="!readonly">Save changes</app-primary-button>
        <saved-indicator :saved="saved" />
      </v-form>
    </v-col>
  </v-row>
</template>

<style scoped>
.table td {
  padding-bottom: 0.5em;
}
.position {
  width: 25%;
}

.count {
  min-width: 8em;
  width: 8em;
}

.description {
  padding-left: 1em;
  font-size: small;
}
</style>

<script>
import { firestore } from "../../modules/firebase"
import * as leagueService from "../../api/110yards/league"
import SavedIndicator from "../SavedIndicator"
import AppSelect from "../inputs/AppSelect.vue"
import AppPrimaryButton from "../buttons/AppPrimaryButton.vue"
import AppTextField from "../inputs/AppTextField.vue"
import AppNumberField from "../inputs/AppNumberField.vue"
import AppFormLabel from "../inputs/AppFormLabel.vue"
import eventBus from "../../modules/eventBus"

export default {
  name: "scoring-settings",
  components: {
    SavedIndicator,
    AppSelect,
    AppPrimaryButton,
    AppTextField,
    AppNumberField,
    AppFormLabel,
  },
  props: {
    leagueId: String,
    leagueStarted: Boolean,
  },
  data() {
    return {
      leagueScoring: {},
      scoringInfo: {},
      saved: false,
    }
  },

  computed: {
    isWeek1() {
      return this.$root.state.current_week == 1
    },
    weekStarted() {
      return this.$root.anyLocks
    },
    readonly() {
      // return this.weekStarted
      return false
    },
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
    submit() {
      let valid = this.$refs.form.validate()
      if (!valid) {
        eventBus.$emit("show-error", "All fields are required")
        return
      }

      this.save()
    },

    async save() {
      await leagueService.updateScoringConfig(this.leagueId, this.leagueScoring)

      this.saved = true
    },

    configureReferences() {
      let leagueScoringRef = firestore.collection("league").doc(this.leagueId).collection("config").doc("scoring")

      this.$bind("leagueScoring", leagueScoringRef)
      this.$bind("scoringInfo", firestore.doc("public/scoring_info"))
    },
  },
  watch: {
    leagueId: {
      immediate: true,
      async handler(leagueId) {
        if (leagueId == null) return
        this.configureReferences()
      },
    },
    leagueScoring: {
      deep: true,
      handler(leagueScoring) {
        this.saved = false
      },
    },
  },
}
</script>
