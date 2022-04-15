<template>
  <v-card v-if="league">
    <v-card-title> League Notes</v-card-title>
    <v-card-subtitle>
      League notes are used to share information between league members (eg: payouts or house rules). Only the
      commissioner can set league notes.
    </v-card-subtitle>
    <v-card-text>
      <app-text-area readonly :value="league.notes" />
    </v-card-text>
  </v-card>
</template>

<script>
import AppTextArea from "../../components/inputs/AppTextArea.vue"
import { firestore } from "../../modules/firebase"

export default {
  components: { AppTextArea },
  props: {
    leagueId: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      league: null,
    }
  },

  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        if (leagueId) {
          let path = `league/${leagueId}`
          let ref = firestore.doc(path)
          this.$bind("league", ref)
        }
      },
    },
  },
}
</script>
