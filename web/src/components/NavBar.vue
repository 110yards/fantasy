<template>
  <nav class="navbar navbar-expand-md navbar-dark">
    <button type="button" class="navbar-toggler" data-toggle="collapse" data-target="#navbar-left">
      <span class="navbar-toggler-icon"></span>
    </button>
    <router-link to="/" class="navbar-brand">
      <img class="logo-small" src="@/assets/img/football-white.png" alt="110 yards" />
      <label class="sr-only">Home</label>
    </router-link>
    <div id="navbar-left" class="navbar-collapse collapse" :class="visible ? 'show' : null" @click="visible = !visible">
      <div class="nav navbar-nav">
        <router-link v-if="leagueId" class="nav-item nav-link" :to="{ name: 'league', params: { leagueId: leagueId } }"
          >League</router-link
        >

        <router-link
          v-if="leagueId && userId"
          class="nav-item nav-link"
          :to="{
            name: 'roster',
            params: { leagueId: leagueId, rosterId: userId },
          }"
          >My Team</router-link
        >

        <router-link
          v-if="leagueId"
          class="nav-item nav-link"
          :to="{ name: 'league-players', params: { leagueId: leagueId } }"
          >Players</router-link
        >

        <router-link class="nav-item nav-link" to="/faq">FAQ</router-link>

        <router-link v-if="isAdmin" class="nav-item nav-link" to="/admin">Admin</router-link>
      </div>
      <div class="nav navbar-nav ml-auto">
        <router-link id="login" v-if="isAnonymous" class="nav-item nav-link" to="/login">Log in</router-link>
        <!-- <span class="nav-item navbar-text">{{username}}</span> -->
        <a id="logout" v-if="!isAnonymous" class="nav-item nav-link" href="#" @click="logOut">Log out</a>
      </div>
    </div>
    <!-- </div> -->
  </nav>
</template>

<style scoped>
.navbar {
  background-color: var(--color-primary);
  background-image: none;
}

.navbar img.logo-small {
  height: 40px;
}

.navbar-brand {
  margin-top: -8px;
}

.navbar-inverse .navbar-nav > li > a {
  color: #cccccc;
}
</style>

<script>
import { auth } from "../modules/firebase"

// TODO: navbar needs to close when I click a link
export default {
  name: "nav-bar",
  data() {
    return {
      visible: false,
      rosterId: null,
    }
  },
  computed: {
    isAnonymous() {
      return this.$store.state.isAnonymous
    },
    username() {
      return this.isAnonymous ? "" : this.$store.state.currentUser.displayName
    },
    userId() {
      return this.isAnonymous ? "" : this.$store.state.uid
    },
    leagueId() {
      return this.$store.state.currentLeagueId
    },
    isAdmin() {
      return this.$store.state.isAdmin
    },
  },
  methods: {
    async logOut() {
      await auth.signOut()
      this.$router.replace("/")
    },
  },
}
</script>
