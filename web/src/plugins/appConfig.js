const config = {
  season: process.env.VUE_APP_SEASON,
  league: {
    maxTeams: 8,
  },
}

export default {
  install(Vue, _) {
    Vue.prototype.$appConfig = config
  },
}
