<template>
  <div v-if="isAdmin">
    <v-simple-table>
      <template>
        <thead>
          <tr>
            <th></th>
            <th>Email</th>
            <th>Last sign in</th>
            <th>Actions</th>
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
              <td>
                <v-menu v-if="!user.is_admin" offset-y>
                  <template v-slot:activator="{ on }">
                    <v-btn icon v-on="on">
                      <v-icon>mdi-dots-vertical</v-icon>
                    </v-btn>
                  </template>

                  <v-list>
                    <v-list-item v-if="isMod(user)" @click="revokeMod(user)">
                      <v-list-item-title>Revoke mod status</v-list-item-title>
                    </v-list-item>

                    <v-list-item v-else @click="grantMod(user)">
                      <v-list-item-title>Grant mod status</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </td>
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
import { makeMod, removeMod } from "../../api/110yards/user"
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
    isMod(user) {
      return user.is_mod
    },
    grantMod(user) {
      makeMod(user.id)
    },
    revokeMod(user) {
      removeMod(user.id)
    },
  },
  created() {
    let ref = firestore.collection("user")
    this.$bind("users", ref)
  },
}
</script>
