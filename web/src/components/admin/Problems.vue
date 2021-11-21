<template>
  <v-simple-table>
    <template>
      <thead>
        <tr>
          <th>Name</th>
          <th>ID</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="league in problemLeagues" :key="league.id">
          <td>{{ league.name }}</td>
          <td>{{ league.id }}</td>
          <td><app-primary-button @click="createSubscriptions(league)">Fix</app-primary-button></td>
        </tr>
      </tbody>
    </template>
  </v-simple-table>
</template>

<script>
import { problems } from "../../api/110yards/admin"
import AppPrimaryButton from "../buttons/AppPrimaryButton.vue"
import { fixSubscriptions } from "../../api/110yards/league"

export default {
  components: { AppPrimaryButton },
  name: "problems",
  data() {
    return {
      problemLeagues: [],
    }
  },

  computed: {},

  methods: {
    async getData() {
      this.problemLeagues = await problems()
    },

    async createSubscriptions(league) {
      let command = {
        league_id: league.id,
      }

      await fixSubscriptions(command)
      this.getData()
    },
  },

  created() {
    this.getData()
  },
}
</script>
