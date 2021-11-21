module.exports = {
  configureWebpack: {
    devtool: "source-map",
  },

  transpileDependencies: ["vuetify"],
  css: {
    extract: true,
  },
}
