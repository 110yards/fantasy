<template>
  <v-row>
    <v-alert v-if="hasDuplicates" type="error" class="mx-3">
      This league has been affected by a bug which allowed rosters to show up multiple times in the draft order. Click
      the update button to fix the problem.
    </v-alert>

    <v-alert v-if="blankEntries" type="error" class="mx-3">
      This league has been affected by a bug which caused removed teams to remain in the draft order. Click the update
      button to fix the problem.
    </v-alert>

    <v-col md="6" col="12">
      <ol>
        <draggable v-model="draftOrder" @start="drag = true" @end="drag = false">
          <li v-for="element in draftOrder" :key="element.roster_id" class="roster">
            {{ getRosterName(element.roster_id) }}
            <v-icon class="float-right">mdi-menu</v-icon>
          </li>
        </draggable>
      </ol>
      <app-primary-button type="button" @click="save"> Update </app-primary-button>
      <saved-indicator :saved="saved" />
    </v-col>
  </v-row>
</template>

<style scoped>
.roster {
  margin: 0.5em;
  padding: 0.5em;
  border: 1px solid var(--bg-color-secondary);
  border-radius: 8px;
  background-color: var(--bg-color-secondary);
  cursor: grabbing;
}

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

export default {
  name: "draft-order",
  components: {
    draggable,
    SavedIndicator,
    AppPrimaryButton,
    AppTextField,
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

    hasDuplicates() {
      let entries = this.draftOrder.length
      let uniqueEntries = [...new Set(this.draftOrder.map(x => x.roster_id))].length

      return entries !== uniqueEntries
    },

    blankEntries() {
      return this.draftOrder.length != this.rosters.length
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

        let ref = firestore.collection("league").doc(league.id).collection("roster")

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
