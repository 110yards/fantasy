<template>
  <div v-if="isAdmin">
    <v-simple-table>
      <template>
        <thead>
          <tr>
            <th></th>
            <th>Email</th>
            <th>Last sign in</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="user in users" :key="user.id">
            <template v-if="!toDelete || toDelete == league">
              <td>
                <v-chip v-if="user.is_admin" color="red">Admin</v-chip>
                <v-chip v-if="user.is_mod" color="orange">Mod</v-chip>
              </td>
              <td>{{ user.email }}</td>
              <td>{{ user.last_sign_in ? formatDate(user.last_sign_in.toDate()) : "Never" }}</td>
              <td></td>
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
import { shortDate } from "../../modules/formatter"

export default {
  name: "Users",

  components: {
    AppPrimaryButton,
    AppDefaultButton,
  },
  data() {
    return {
      users: null,
      toDelete: null,
    }
  },

  computed: {
    isAdmin() {
      return this.$store.state.isAdmin
    },
  },

  methods: {
    formatDate(date) {
      return shortDate(date)
    },
  },

  created() {
    let ref = firestore.collection("user")
    this.$bind("users", ref)
  },
}
</script>
