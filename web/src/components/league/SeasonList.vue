<template>
  <v-select :full-width="false" v-model="selectedSeason" outlined dense :items="items" @change="viewSeason" />
</template>

<script>
import { firestore } from "../../modules/firebase"
import AppSelect from "../inputs/AppSelect.vue"

export default {
  components: { AppSelect },

  props: {
    league: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      seasons: null,
      selectedSeason: this.$root.state.current_season,
    }
  },

  computed: {
    hasSeasons() {
      return this.seasons && this.seasons.length > 0
    },

    currentSeason() {
      return this.$root.state.current_season
    },

    items() {
      let current = [this.currentSeason]

      if (!this.seasons) return current

      let past = this.seasons.map(x => x.id)
      return current.concat(past)
    },
  },

  methods: {
    viewSeason() {
      if (this.selectedSeason == this.currentSeason) return
      this.$router.push(`/league/${this.league.id}/season/${this.selectedSeason}`)
    },

    configureReferences() {
      if (!this.league) return

      let path = `league/${this.league.id}/seasons`
      let ref = firestore.collection(path)
      this.$bind("seasons", ref)
    },
  },

  watch: {
    league: {
      immediate: true,
      handler(league) {
        this.configureReferences()
      },
    },
  },
}
</script>
