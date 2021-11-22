import Vue from "vue"
import VueRouter from "vue-router"
import { routes } from "./routes"
import { auth, getCurrentUser } from "../firebase"
import store from "../store"

Vue.use(VueRouter)

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes,
  scrollBehavior: function (to, from, savedPosition) {
    if (to.hash) {
      return { selector: to.hash }
    } else {
      return { x: 0, y: 0 }
    }
  },
})

router.beforeEach(async (to, from, next) => {
  let ok = checkAuth(to, next)

  if (ok) {
    setLeagueId(to)
    next()
  }
})

async function checkAuth(to, next) {
  let allowAnonymous = to.matched.some(record => record.meta.anonymous)
  let user = await getCurrentUser()

  let ok = allowAnonymous || user != null

  let requireAdmin = to.matched.some(record => record.meta.admin)
  if (requireAdmin) {
    ok = store.state.isAdmin
  }

  if (!ok) {
    next({ name: "login", query: { returnUrl: to.fullPath } })
  }

  return ok
}

function setLeagueId(to) {
  store.dispatch("loadLeague", to.params.leagueId)
}

export default router
