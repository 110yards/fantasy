<template>
  <div v-if="enableDraft" class="draft-button my-2">
    <app-primary-button v-if="canStartDraft" v-on:click="startDraft" class="btn btn-primary">
      Start Draft
    </app-primary-button>
    <app-primary-button v-if="canResumeDraft" class="btn btn-primary" v-on:click="goToDraft">
      Resume Draft
    </app-primary-button>
    <app-primary-button v-if="canJoinDraft" class="btn btn-primary" v-on:click="goToDraft">
      Join Draft
    </app-primary-button>
  </div>
</template>

<style scoped></style>

<script>
import { draftState } from "../../api/110yards/constants"
import * as leagueService from "../../api/110yards/league"
import AppPrimaryButton from "../buttons/AppPrimaryButton.vue"

export default {
  name: "start-draft",
  components: { AppPrimaryButton },
  props: {
    league: {},
  },
  computed: {
    isCommissioner() {
      if (this.league == null || this.$store.state.uid == null) return false

      return this.league.commissioner_id == this.$store.state.uid
    },

    enableDraft() {
      return this.$root.enableDraft
    },

    canStartDraft() {
      return this.isCommissioner && this.league.draft_state == draftState.NotStarted && this.league.schedule_generated
    },
    canResumeDraft() {
      return this.isCommissioner && this.league.draft_state == draftState.InProgress
    },
    canJoinDraft() {
      return !this.isCommissioner && this.league.draft_state == draftState.InProgress
    },

    showDraftNotReadyTip() {
      return this.isCommissioner && !this.canStartDraft
    },
  },

  methods: {
    async startDraft() {
      if (!this.canStartDraft) return

      let result = await leagueService.beginDraft(this.$store.state.currentUser, this.league.id)

      if (result.success) {
        this.goToDraft()
      }
    },
    goToDraft() {
      this.$router.push({
        name: "draft",
        params: { leagueId: this.league.id },
      })
    },
  },
}
</script>
