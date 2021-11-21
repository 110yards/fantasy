<template>
  <v-row>
    <v-col md="6" col="12">
      <v-form ref="form" @submit.prevent="save()">
        <v-simple-table>
          <template v-slot:default>
            <thead>
              <tr>
                <th>Roster</th>
                <th>Budget</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="roster in draftOrder" :key="roster.id">
                <td>{{ getRosterName(roster.roster_id) }}</td>
                <td class="budget">
                  <app-number-field type="number" v-model="roster.budget" />
                </td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>

        <app-primary-button>Save changes</app-primary-button>
        <saved-indicator :saved="saved" />
      </v-form>
    </v-col>
  </v-row>
</template>

<style>
.budget .v-input__control {
  width: 5em;
}
</style>

<script>
import { firestore } from "../../modules/firebase"
import draggable from "vuedraggable"
import SavedIndicator from "../SavedIndicator"
import * as leagueService from "../../api/110yards/league"
import AppPrimaryButton from "../buttons/AppPrimaryButton.vue"
import AppTextField from "../inputs/AppTextField.vue"
import { draftType } from "../../api/110yards/constants"
import AppNumberField from "../inputs/AppNumberField.vue"

export default {
  name: "draft-order",
  components: {
    draggable,
    SavedIndicator,
    AppPrimaryButton,
    AppTextField,
    AppNumberField,
  },
  props: {
    league: Object,
  },
  data() {
    return {
      rosters: [],
      draftOrder: [],
      saved: false,
    }
  },
  computed: {
    showBudgets() {
      return this.league.draft_type == draftType.Auction
    },
  },
  methods: {
    getRosterName(rosterId) {
      let roster = this.rosters.filter(r => r.id == rosterId)[0]

      return roster ? roster.name : null
    },
    async save() {
      let user = this.$store.state.currentUser

      let command = {
        draft_order: this.draftOrder,
      }

      await leagueService.updateDraftOrder(user, this.league.id, command)
      this.saved = true
    },
  },
  watch: {
    league: {
      immediate: true,
      handler(league) {
        if (!league) return

        let ref = firestore
          .collection("league")
          .doc(league.id)
          .collection("roster")

        this.$bind("rosters", ref)
      },
    },
    rosters: {
      immediate: true,
      handler(rosters) {
        if (!rosters || rosters.length == 0) return

        let draftOrder = []

        this.league.draft_order.forEach(i => {
          draftOrder.push(i)
        })

        this.draftOrder = draftOrder
      },
    },
    draftOrder: {
      deep: true,
      handler(draftOrder) {
        this.saved = false
      },
    },
  },
}
</script>
