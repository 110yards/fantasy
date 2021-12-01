// vetur.config.js
/** @type {import('vls').VeturConfig} */
module.exports = {
  // **optional** default: `{}`
  // override vscode settings part
  // Notice: It only affects the settings used by Vetur.
  settings: {
    "vetur.useWorkspaceDependencies": true,
    "vetur.validation.interpolation": false,
  },
  // **optional** default: `[{ root: './' }]`
  // support monorepos
  projects: [
    //   './packages/repo2', // shorthand for only root.
    {
      // **required**
      // Where is your project?
      // It is relative to `vetur.config.js`.
      root: "./web",
      // **optional**
      // Where is Javascript config file in the project?
      // It is relative to root property.
      jsconfig: "..",
      // **optional** default: `[]`
      // Register globally Vue component glob.
      // If you set it, you can get completion by that components.
      // It is relative to root property.
      // Notice: It won't actually do it. You need to use `require.context` or `Vue.component`
      globalComponents: ["./web/src/**/*.vue"],
    },
  ],
}
