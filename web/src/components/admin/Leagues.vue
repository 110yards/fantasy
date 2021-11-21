<template>
  <div v-if="isAdmin && leagues">
    <v-alert type="warning" v-if="toDelete">Delete this league?</v-alert>

    <v-simple-table>
      <template>
        <thead>
          <tr>
            <th></th>
            <th>ID</th>
            <th>Name</th>
            <th>Active</th>
            <!-- <th></th> -->
          </tr>
        </thead>

        <tbody>
          <tr v-for="league in leagues" :key="league.id">
            <template v-if="!toDelete || toDelete == league">
              <td>
                <v-btn icon :to="{ name: 'league', params: { leagueId: league.id } }">
                  <v-icon>mdi-link</v-icon>
                </v-btn>
              </td>
              <td>{{ league.id }}</td>
              <td>{{ league.name }}</td>
              <td>
                <v-chip color="green" v-if="league.draft_state == 'completed'">
                  <v-icon>mdi-check</v-icon>
                </v-chip>
              </td>
              <!-- <td>
                <app-default-button v-if="!toDelete" @click="toDelete = league">Delete</app-default-button>
                <app-default-button v-if="toDelete" @click="deleteLeague(league)">Yes, delete</app-default-button>
                <app-primary-button class="ml-2" v-if="toDelete" @click="toDelete = null"
                  >No, cancel</app-primary-button
                >
              </td> -->
            </template>
          </tr>
        </tbody>
      </template>
    </v-simple-table>
  </div>
</template>

<script>
import { firestore } from "../../modules/firebase"
import AppDefaultButton from "../buttons/AppDefaultButton.vue"
import AppPrimaryButton from "../buttons/AppPrimaryButton.vue"

export default {
  name: "Leagues",

  components: {
    AppPrimaryButton,
    AppDefaultButton,
  },
  data() {
    return {
      leagues: null,
      toDelete: null,
    }
  },

  computed: {
    isAdmin() {
      return this.$store.state.isAdmin
    },
  },

  methods: {
    deleteLeague(league) {},
  },

  created() {
    let ref = firestore.collection("league")
    this.$bind("leagues", ref)
  },
}
</script>
