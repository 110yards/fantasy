import Vue from "vue"
import Vuex from "vuex"
import { signIn } from "../../api/110yards/user"
import { firestore } from "../firebase"

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    currentUser: null,
    currentProfile: null,
    isAnonymous: true,
    uid: null,
    currentLeagueId: null,
    isAdmin: false,
    systemState: null,
    isMod: false,
  },
  mutations: {
    logIn(state, data) {
      state.currentUser = data.user
      state.currentProfile = data.profile
      state.isAnonymous = false
      state.uid = data.user.uid
      state.isAdmin = data.profile.is_admin
      state.systemState = data.systemState
      state.isMod = data.profile.is_mod
    },
    logOut(state) {
      state.currentUser = null
      state.currentProfile = null
      state.isAnonymous = true
      state.uid = null
      state.isAdmin = false
      state.isMod = false
    },
    setCurrentLeagueId(state, leagueId) {
      state.currentLeagueId = leagueId
    },
  },
  actions: {
    async updateUser({ dispatch, commit }, user) {
      if (user) {
        let systemState = (await firestore.doc("admin/state").get()).data()
        let profile = (await firestore.doc(`user/${user.uid}`).get()).data()

        await signIn(user)
        commit("logIn", { user: user, systemState: systemState, profile: profile })
      } else {
        commit("logOut")
      }
    },

    loadLeague({ commit, state }, leagueId) {
      let changingLeague = leagueId !== state.currentLeagueId

      if (changingLeague) {
        commit("setCurrentLeagueId", leagueId)
      }
    },
  },
  modules: {},
  getters: {
    user(state) {
      return state.user
    },
  },
})
