<template>
  <v-card>
    <v-card-text>
      <v-carousel
        v-if="schedule"
        v-model="selectedWeekIndex"
        hide-delimiters
        :show-arrows-on-hover="true"
        height="auto"
      >
        <v-carousel-item v-for="week in schedule.weeks" :key="week.week_number">
          <v-sheet>
            <v-row>
              <v-col cols="12" class="text-center">
                {{ week.heading }}
              </v-col>
            </v-row>
            <matchup-preview
              v-for="matchup in week.matchups"
              class="matchup"
              :key="matchup.id"
              :leagueId="leagueId"
              :matchup="matchup"
              :weekNumber="week.week_number"
            />
          </v-sheet>
        </v-carousel-item>
      </v-carousel>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.matchup {
  border-bottom: 1px solid var(--bg-color-primary);
}
</style>

<script>
import MatchupPreview from "./MatchupPreview.vue"
import { firestore } from "../../modules/firebase"

export default {
  components: { MatchupPreview },
  name: "schedule",
  props: {
    leagueId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      selectedWeekIndex: null,
      schedule: null,
    }
  },

  computed: {
    currentWeek() {
      return this.$root.state.current_week
    },
  },

  methods: {
    isFirstWeek(week) {
      return this.weeks != null && this.weeks[0].week_number == week.week_number
    },
    isLastWeek(week) {
      return this.weeks != null && this.weeks[this.weeks.length - 1].week_number == week.week_number // todo: implement
    },
  },

  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        let ref = firestore.collection("league").doc(leagueId).collection("config").doc("schedule")

        this.$bind("schedule", ref)
      },
    },

    selectedWeekIndex: {
      handler(selectedWeekIndex) {
        if (this.schedule != null && selectedWeekIndex >= this.schedule.weeks.length) {
          this.selectedWeekIndex = this.schedule.weeks.length - 1
        }
      },
    },

    schedule: {
      handler(schedule) {
        if (schedule != null && this.selectedWeekIndex >= this.schedule.weeks.length) {
          this.selectedWeekIndex = this.schedule.weeks.length - 1
        }
      },
    },

    currentWeek: {
      immediate: true,
      handler(currentWeek) {
        this.selectedWeekIndex = currentWeek - 1
      },
    },
  },
}
</script>
