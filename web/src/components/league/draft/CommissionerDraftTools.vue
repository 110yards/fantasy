<template>
  <v-card>
    <v-card-title>Commissioner tools</v-card-title>
    <v-card-subtitle v-if="draft.is_paused && !endDraftClicked">
      The draft is currently paused. While paused, you may undo picks or reset the draft. To reset the draft, you must
      first undo all picks.
      <!-- todo: update message to say "you may pick for any roster, once that is supported" -->
    </v-card-subtitle>
    <v-card-text v-if="!draft.is_paused">
      <app-default-button @click="pauseDraft">Pause Draft</app-default-button>
    </v-card-text>
    <v-card-text v-if="draft.is_paused && !endDraftClicked">
      <app-primary-button class="mr-2" v-if="draft.is_paused" @click="resumeDraft">Resume Draft</app-primary-button>
      <app-default-button class="mr-2" @click="undoLastPick">Undo Last Pick</app-default-button>
      <app-default-button class="mr-2" @click="resetDraft">Reset Draft</app-default-button>
      <app-default-button class="mr-2" v-if="isAuction">Clear nomination</app-default-button>
      <app-default-button class="mr-2" @click="confirmEndDraft">End Draft</app-default-button>
    </v-card-text>

    <v-card-subtitle v-if="endDraftClicked">
      Are you sure you want to end the draft early? This cannot be undone.
    </v-card-subtitle>
    <v-card-text v-if="endDraftClicked">
      <app-primary-button class="mr-2" v-if="endDraftClicked" @click="endDraftClicked = false"
        >No, continue draft</app-primary-button
      >
      <app-default-button class="mr-2" v-if="endDraftClicked" @click="endDraft">
        Yes, end draft early
      </app-default-button>
    </v-card-text>
  </v-card>
</template>

<script>
import { draftType } from "../../../api/110yards/constants"
import { endDraft, pauseDraft, resetDraft, resumeDraft, undoLastPick } from "../../../api/110yards/league"
import eventBus from "../../../modules/eventBus"
import AppDefaultButton from "../../buttons/AppDefaultButton.vue"
import AppPrimaryButton from "../../buttons/AppPrimaryButton.vue"

export default {
  components: { AppPrimaryButton, AppDefaultButton },
  name: "commissioner-draft-tools",
  props: {
    draft: {
      type: Object,
      required: true,
    },
    leagueId: {
      type: String,
      required: true,
    },
    previousSlot: {
      type: Object,
      required: false,
      default: null,
    },
  },
  data() {
    return {
      endDraftClicked: false,
    }
  },
  computed: {
    currentUser() {
      return this.$store.state.currentUser
    },

    isAuction() {
      return this.draft.draft_type == draftType.Auction
    },
  },
  methods: {
    async pauseDraft() {
      let result = await pauseDraft(this.currentUser, this.leagueId)
    },

    async resumeDraft() {
      let result = await resumeDraft(this.currentUser, this.leagueId)
    },

    async undoLastPick() {
      if (this.previousSlot == null) {
        eventBus.$emit("show-error", "No picks have been made yet")
        return
      }

      await undoLastPick(this.currentUser, this.leagueId)
    },

    async resetDraft() {
      if (this.previousSlot != null) {
        eventBus.$emit("show-error", "You must undo all picks before resetting the draft")
        return
      }

      await resetDraft(this.leagueId)
    },

    confirmEndDraft() {
      this.endDraftClicked = true
    },

    async endDraft() {
      await endDraft(this.leagueId)
    },
  },
}
</script>
