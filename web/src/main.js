import Vue from "vue"
import App from "./App.vue"
import router from "./modules/router"
import store from "./modules/store"
import eventBus from "./modules/eventBus"
import { firestorePlugin, rtdbPlugin } from "vuefire"
import "firebase/database"
import "firebase/auth"
import "firebase/firestore"
import switches from "./mixins/switches"

import "./assets/css/site.css"
import "./assets/css/tables.css"
import "./assets/css/buttons.css"
import "./assets/css/team-flair.css"
import vuetify from "./plugins/vuetify"
import appConfig from "./plugins/appConfig"
import rosterPositions from "./mixins/rosterPositions"
import opponents from "./mixins/opponents"
import state from "./mixins/state"
import league from "./mixins/league"
import teamGames from "./mixins/teamGames"

Vue.config.productionTip = false

Vue.use(firestorePlugin)
Vue.use(rtdbPlugin)
Vue.use(appConfig)

Vue.prototype.$eventBus = eventBus

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App),
  mixins: [switches, rosterPositions, opponents, state, league, teamGames],
}).$mount("#app")
