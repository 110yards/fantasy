<template>
  <v-select :full-width="false" v-model="selectedSeason" outlined dense :items="items" @change="viewSeason" />
</template>

<script>
import { firestore } from "../../modules/firebase"
import AppSelect from "../inputs/AppSelect.vue"

export default {
  components: { AppSelect },

  props: {
    leagueId: {
      type: String,
      required: true,
    },
    season: {
      type: String,
      required: false,
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
      if (this.selectedSeason == this.currentSeason) {
        this.$router.push(`/league/${this.leagueId}`)
      } else {
        this.$router.push(`/league/${this.leagueId}/season/${this.selectedSeason}`)
      }
    },

    configureReferences() {
      if (!this.leagueId) return

      let path = `league/${this.leagueId}/seasons`
      let ref = firestore.collection(path)
      this.$bind("seasons", ref)
    },
  },

  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        this.configureReferences()
      },
    },

    season: {
      immediate: true,
      handler(season) {
        if (season) {
          this.selectedSeason = season
        }
      },
    },
  },
}
</script>
