<template>
  <div>
    <auction-draft
      v-if="isAuction"
      :leagueId="leagueId"
      :draft="draft"
      :rosters="rosters"
      :isCommissioner="isCommissioner"
    />

    <snake-draft
      v-if="isSnake"
      :leagueId="leagueId"
      :draft="draft"
      :rosters="rosters"
      :isCommissioner="isCommissioner"
    />

    <commissioner-draft
      v-if="isCommissionerDraft"
      :leagueId="leagueId"
      :draft="draft"
      :rosters="rosters"
      :isCommissioner="isCommissioner"
    />
  </div>
</template>

<script>
import { firestore } from "../../../modules/firebase"
import { draftState, draftType } from "../../../api/110yards/constants"
import AuctionDraft from "../../../components/league/draft/AuctionDraft.vue"
import SnakeDraft from "../../../components/league/draft/SnakeDraft.vue"
import CommissionerDraft from "../../../components/league/draft/CommissionerDraft.vue"
import eventBus from "../../../modules/eventBus"

export default {
  name: "draft",
  components: {
    AuctionDraft,
    SnakeDraft,
    CommissionerDraft,
  },
  props: {
    leagueId: String,
  },
  data() {
    return {
      draft: null,
      rosters: null,
      league: null,
    }
  },
  computed: {
    isCommissioner() {
      if (this.draft == null || this.$store.state.uid == null) return false

      return this.draft.commissioner_id == this.$store.state.uid
    },

    currentRosterId() {
      return this.$store.state.uid
    },

    currentUser() {
      return this.$store.state.currentUser
    },

    isAuction() {
      return this.draft != null && this.draft.draft_type == draftType.Auction
    },

    isSnake() {
      return this.draft != null && this.draft.draft_type == draftType.Snake
    },

    isCommissionerDraft() {
      return this.draft != null && this.draft.draft_type == draftType.Commissioner
    },

    isComplete() {
      return this.draft != null && this.draft.complete
    },

    wasReset() {
      return this.league != null && this.league.draft_state == draftState.Reset
    },
  },

  methods: {
    configureBindings() {
      let leagueRef = firestore.collection("league").doc(this.leagueId)
      this.$bind("league", leagueRef)

      let draftRef = leagueRef.collection("config").doc("draft")
      this.$bind("draft", draftRef)

      let rostersRef = leagueRef.collection("roster")
      this.$bind("rosters", rostersRef)
    },
  },

  watch: {
    isComplete: {
      immediate: true,
      handler(isComplete) {
        if (isComplete) {
          eventBus.$emit("show-success", "Draft complete!")
          this.$router.push({ name: "league", params: { leagueId: this.leagueId } })
        }
      },
    },

    wasReset: {
      handler(wasReset) {
        if (wasReset) {
          eventBus.$emit("show-error", "The draft was reset")
          this.$router.push({ name: "league", params: { leagueId: this.leagueId } })
        }
      },
    },

    leagueId: {
      immediate: true,
      handler(leagueId) {
        if (!leagueId) return

        this.configureBindings()
      },
    },

    currentRosterId: {
      immediate: true,
      handler(currentRosterId) {
        this.selectedRosterId = currentRosterId != null ? currentRosterId : null
      },
    },
  },
}
</script>
