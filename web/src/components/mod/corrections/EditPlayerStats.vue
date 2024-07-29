<template>
  <div v-if="player" class="mb-2">
    <div>
      {{ player.display_name }}
      <a v-if="playerGame.manual_override && !resetting" class="pl-1" href="#" @click.prevent="confirmRevert()"
        >Revert</a
      >
    </div>
    <span :class="textClass">{{ text }}</span>

    <a v-if="!editing" class="pl-1" href="#" @click.prevent="startEditing()">Edit</a>
    <v-container v-if="editing">
      <v-row>
        <h4>Passing</h4>
      </v-row>
      <v-row>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.pass_completions}`"
            @input="value => (editedStats.pass_completions = value)"
            label="COMP"
          />
        </v-col>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.pass_attempts}`"
            @input="value => (editedStats.pass_attempts = value)"
            label="ATT"
          />
        </v-col>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.pass_net_yards}`"
            @input="value => (editedStats.pass_net_yards = value)"
            label="YDS"
          />
        </v-col>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.pass_touchdowns}`"
            @input="value => (editedStats.pass_touchdowns = value)"
            label="TD"
          />
        </v-col>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.pass_interceptions}`"
            @input="value => (editedStats.pass_interceptions = value)"
            label="INT"
          />
        </v-col>
      </v-row>

      <v-row>
        <h4>Rushing</h4>
      </v-row>

      <v-row>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.rush_attempts}`"
            @input="value => (editedStats.rush_attempts = value)"
            label="ATT"
          />
        </v-col>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.rush_net_yards}`"
            @input="value => (editedStats.rush_net_yards = value)"
            label="YDS"
          />
        </v-col>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.rush_touchdowns}`"
            @input="value => (editedStats.rush_touchdowns = value)"
            label="TD"
          />
        </v-col>
      </v-row>

      <v-row>
        <h4>Receiving</h4>
      </v-row>

      <v-row>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.receive_caught}`"
            @input="value => (editedStats.receptions = value)"
            label="REC"
          />
        </v-col>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.receive_yards}`"
            @input="value => (editedStats.receive_yards = value)"
            label="YDS"
          />
        </v-col>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.receive_touchdowns}`"
            @input="value => (editedStats.receive_touchdowns = value)"
            label="TD"
          />
        </v-col>
      </v-row>

      <v-row>
        <h4>Defense</h4>
      </v-row>

      <v-row>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.tackles_defensive}`"
            @input="value => (editedStats.tackles_defensive = value)"
            label="TKL"
          />
        </v-col>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.tackles_special_teams}`"
            @input="value => (editedStats.tackles_special_teams = value)"
            label="STT"
          />
        </v-col>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.sacks_qb_made}`"
            @input="value => (editedStats.sacks_qb_made = value)"
            label="SACK"
          />
        </v-col>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.interceptions}`"
            @input="value => (editedStats.interceptions = value)"
            label="INT"
          />
        </v-col>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.fumbles_recovered}`"
            @input="value => (editedStats.fumbles_recovered = value)"
            label="FR"
          />
        </v-col>
      </v-row>

      <v-row>
        <h4>Kicking</h4>
      </v-row>

      <v-row>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.field_goal_made}`"
            @input="value => (editedStats.field_goal_made = value)"
            label="FGM"
          />
        </v-col>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.field_goal_attempts}`"
            @input="value => (editedStats.field_goal_attempts = value)"
            label="FGA"
          />
        </v-col>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.one_point_converts_made}`"
            @input="value => (editedStats.one_point_converts_made = value)"
            label="XP"
          />
        </v-col>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.one_point_converts_attempts}`"
            @input="value => (editedStats.one_point_converts_attempts = value)"
            label="XPA"
          />
        </v-col>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.field_goal_singles}`"
            @input="value => (editedStats.field_goal_singles = value)"
            label="Singles"
          />
        </v-col>
      </v-row>

      <v-row>
        <h4>Punting</h4>
      </v-row>

      <v-row>
        <v-col cols="4" md="2">
          <AppTextField :value="`${editedStats.punts}`" @input="value => (editedStats.punts = value)" label="Punts" />
        </v-col>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.punt_gross_yards}`"
            @input="value => (editedStats.punt_gross_yards = value)"
            label="Yards"
          />
        </v-col>
        <v-col cols="4" md="2">
          <AppTextField
            :value="`${editedStats.punt_singles}`"
            @input="value => (editedStats.punt_singles = value)"
            label="Singles"
          />
        </v-col>
      </v-row>

      <AppPrimaryButton @click="save">Save</AppPrimaryButton>
      <AppDefaultButton class="ml-2" @click="cancel()">Cancel</AppDefaultButton>
    </v-container>
    <div v-if="reverting">
      <p>Undo overrides and revert to imported game stats?</p>
      <AppPrimaryButton @click="revert">Yes</AppPrimaryButton>
      <AppDefaultButton class="ml-2" @click="cancel()">No</AppDefaultButton>
    </div>
  </div>
</template>

<script>
import { firestore } from "../../../modules/firebase/index.js"
import AppTextField from "../../inputs/AppTextField.vue"
import AppPrimaryButton from "../../buttons/AppPrimaryButton.vue"
import AppDefaultButton from "../../buttons/AppDefaultButton.vue"
import { revertPlayerGame, updatePlayerGame } from "../../../api/110yards/mod.js"

export default {
  name: "EditPlayerStats",
  components: { AppTextField, AppPrimaryButton, AppDefaultButton },
  props: {
    season: {
      type: Number,
      required: true,
    },
    text: {
      type: String,
      required: true,
    },
    playerGame: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      player: null,
      editedStats: null,
      reverting: false,
    }
  },
  computed: {
    editing() {
      return this.editedStats !== null
    },
    textClass() {
      return this.playerGame.manual_override ? "font-italic" : ""
    },
  },
  methods: {
    startEditing() {
      this.reverting = false
      this.editedStats = { ...this.playerGame.stats }
    },
    confirmRevert() {
      this.reverting = true
      this.editedStats = null
    },
    cancel() {
      this.reverting = false
      this.editedStats = null
    },
    async getPlayer() {
      if (this.season && this.playerGame) {
        let doc = await firestore.doc(`season/${this.season}/player/${this.playerGame.player_id}`).get()

        this.player = doc.data()
      }
    },
    async save() {
      let command = {
        id: this.playerGame.id,
        season: this.season,
        game_id: this.playerGame.game_id,
        stats: this.editedStats,
      }

      let result = await updatePlayerGame(command)

      if (result.success) {
        this.editedStats = null
      }
    },
    async revert() {
      let command = {
        id: this.playerGame.id,
        season: this.season,
        game_id: this.playerGame.game_id,
      }

      let result = await revertPlayerGame(command)

      if (result.success) {
        this.reverting = false
      }
    },
  },
  watch: {
    playerGame: {
      immediate: true,
      handler(v) {
        this.getPlayer()
      },
    },
    season: {
      immediate: true,
      handler(v) {
        this.getPlayer()
      },
    },
  },
}
</script>
