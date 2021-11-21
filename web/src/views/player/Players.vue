<template>
  <player-list
    :leagueId="leagueId"
    :showActions="showActions"
    :inputFilters="filterPositions"
    :toPositionId="toPositionId"
  />
</template>

<style scoped>
.position-toggle {
  margin-left: 1em;
}

.v-btn.position-filter-active {
  background-color: var(--v-primary_button-base);
}

.player-list >>> th[role="columnheader"] {
  white-space: nowrap;
}
</style>

<script>
import { firestore } from "../../modules/firebase"
import { draftState } from "../../api/110yards/constants"
import PlayerList from "../../components/player/PlayerList.vue"

export default {
  name: "players",
  components: { PlayerList },
  props: {
    leagueId: null,
    filterPositions: {
      type: Array,
      required: false,
    },
    toPositionId: {
      type: Number,
      required: false,
    },
  },

  data() {
    return {
      league: null,
    }
  },

  computed: {
    showActions() {
      return this.league != null ? this.league.draft_state == draftState.Complete : false
    },
  },

  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        if (!leagueId) return

        let leagueRef = firestore.doc(`league/${leagueId}`)
        this.$bind("league", leagueRef)
      },
    },
  },
}
</script>
