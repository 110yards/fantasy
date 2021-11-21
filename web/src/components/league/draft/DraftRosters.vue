<template>
  <div>
    <app-select :items="rosterSelections" v-model="selectedRosterId" label="Rosters" />
    <div class="roster" v-for="roster in rosters" :key="roster.id" v-show="roster.id == selectedRosterId">
      <h4>
        <span v-if="isAuction">${{ roster.draft_budget }}</span>
      </h4>
      <lineup :leagueId="leagueId" :roster="roster" />
    </div>
  </div>
</template>

<script>
import AppSelect from "../../inputs/AppSelect.vue"
import Lineup from "./Lineup.vue"

export default {
  components: { AppSelect, Lineup },
  name: "draft-rosters",
  props: {
    isAuction: {
      type: Boolean,
      required: true,
    },
    rosters: {
      type: Array,
      required: true,
    },
    leagueId: {
      type: String,
      required: true,
    },
    isCommissionerDraft: {
      type: Boolean,
      required: false,
      default: false,
    },
    isCommissioner: {
      type: Boolean,
      required: false,
      default: false,
    },
  },

  data() {
    return {
      selectedRosterId: null,
    }
  },

  computed: {
    currentRosterId() {
      return this.$store.state.uid
    },

    rosterSelections() {
      let showYourTeamLabel = !this.isCommissionerDraft || !this.isCommissioner
      return this.rosters == null
        ? []
        : this.rosters.map(r => {
            return {
              text: showYourTeamLabel && r.id == this.currentRosterId ? "Your team" : r.name,
              value: r.id,
            }
          })
    },
  },

  methods: {
    getRoster(rosterId) {
      return this.rosters.find(r => r.id == rosterId)
    },

    getRosterName(rosterId) {
      let roster = this.getRoster(rosterId)

      return roster != null ? roster.name : ""
    },
  },

  watch: {
    currentRosterId: {
      immediate: true,
      handler(currentRosterId) {
        this.selectedRosterId = currentRosterId
      },
    },

    selectedRosterId: {
      immediate: true,
      handler(selectedRosterId) {
        this.$emit("rosterChange", { rosterId: selectedRosterId, rosterName: this.getRosterName(selectedRosterId) })
      },
    },
  },
}
</script>
