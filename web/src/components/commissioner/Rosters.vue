<template>
  <v-row v-if="leaguePositions && rosterPositions">
    <v-col cols="12">
      <v-form ref="form" @submit.prevent="submit()">
        <app-form-label>Allow Quarterbacks on bench?</app-form-label>
        <v-layout align-center class="mb-8">
          <v-simple-checkbox class="form-check-input" :ripple="false" v-model="leaguePositions.allow_bench_qb" />
          <span>Yes</span>
        </v-layout>

        <app-form-label>Allow Runningbacks on bench?</app-form-label>
        <v-layout align-center class="mb-8">
          <v-simple-checkbox class="form-check-input" :ripple="false" v-model="leaguePositions.allow_bench_rb" />
          <span>Yes</span>
        </v-layout>

        <app-form-label>Allow Kickers on bench?</app-form-label>
        <v-layout align-center class="mb-8">
          <v-simple-checkbox class="form-check-input" :ripple="false" v-model="leaguePositions.allow_bench_k" />
          <span>Yes</span>
        </v-layout>

        <v-alert type="warning" v-if="notLimitingRarePositions">
          Allowing limited position players (QB, RB or K) on bench may allow teams to stockpile and affect league
          balance.
        </v-alert>

        <v-alert type="info" v-else>
          Quarterback, running back and kicker slots are capped at 1 per roster unless they are in a Bye or IR reserve
          slot.
        </v-alert>

        <v-simple-table>
          <template v-slot:default>
            <thead>
              <tr>
                <th>Position</th>
                <th>Count</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="position in rosterPositions" :key="position.id">
                <th class="position">{{ position.display }}</th>
                <td class="count">
                  <app-number-field
                    v-if="!leagueStarted"
                    type="number"
                    v-model="leaguePositions[position.id]"
                    :data-position-id="position.id"
                    :max="getMax(position)"
                  />
                  <app-form-label v-else>{{ leaguePositions[position.id] }}</app-form-label>
                </td>
                <td class="description">{{ position.description }}</td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>

        <app-primary-button v-if="!leagueStarted">Save changes</app-primary-button>
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
import AppCheckBox from "../inputs/AppCheckBox.vue"

export default {
  name: "rosters",
  components: {
    SavedIndicator,
    AppSelect,
    AppPrimaryButton,
    AppTextField,
    AppNumberField,
    AppFormLabel,
    AppCheckBox,
  },

  props: {
    leagueId: String,
    leagueStarted: Boolean,
  },

  data() {
    return {
      leaguePositions: {},
      rosterPositions: [],
      saved: false,
    }
  },

  computed: {
    notLimitingRarePositions() {
      return (
        this.leaguePositions &&
        (this.leaguePositions.allow_bench_qb == true ||
          this.leaguePositions.allow_bench_rb == true ||
          this.leaguePositions.allow_bench_k == true)
      )
    },
  },

  methods: {
    getMax(position) {
      // Don't love this hard coding.
      if (
        (position.id == "qb" && this.leaguePositions.allow_bench_qb) ||
        (position.id == "rb" && this.leaguePositions.allow_bench_rb) ||
        (position.id == "k" && this.leaguePositions.allow_bench_k)
      ) {
        return ""
      }

      return position.max ? position.max.toString() : ""
    },

    submit() {
      let valid = this.$refs.form.validate()
      if (!valid) return

      this.save()
    },

    async save() {
      let user = this.$store.state.currentUser
      await leagueService.updateRosterPositions(user, this.leagueId, this.leaguePositions)

      this.saved = true
    },

    async bindLeague(leagueId) {
      this.leaguePositions = (
        await firestore.collection("league").doc(leagueId).collection("config").doc("positions").get()
      ).data()
    },

    async bindPositions() {
      await this.$bind("rosterPositions", firestore.collection("roster-positions").orderBy("order"))
    },
  },
  watch: {
    leagueId: {
      immediate: true,
      async handler(leagueId) {
        if (leagueId == null) return

        let promises = []
        promises.push(this.bindLeague(leagueId))
        promises.push(this.bindPositions())

        await Promise.all(promises)
      },
    },
    leaguePositions: {
      deep: true,
      handler(leaguePositions) {
        this.saved = false
      },
    },
  },
}
</script>
