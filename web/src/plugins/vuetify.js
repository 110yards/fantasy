import Vue from "vue"
import Vuetify from "vuetify/lib/framework"

Vue.use(Vuetify)
/*
  --text-color: #cccccc;

  --color-primary: #581010;
  --color-secondary: #bf8753;

  --bg-color-primary: #121212;
  --bg-color-secondary: #222222;
  */

export default new Vuetify({
  theme: {
    dark: true,
    options: {
      customProperties: true,
    },
    themes: {
      light: {
        primary: "#581010",
        secondary: "#BF8753",
        anchor: "#BF8753",
        accent: "#82B1FF",
        error: "#FF5252",
        info: "#2196F3",
        success: "#4CAF50",
        warning: "#fb8c00",
      },
      dark: {
        //https://www.color-hex.com/color-palette/30777
        header: "#581010",
        primary: "#bf8753",
        secondary: "#581010",

        primary_button: "#581010",
        primary_button_border: "#BF8753",
        default_button: "#333",
        default_button_border: "#999",

        anchor: "#BF8753",
        accent: "#82B1FF",
        error: "#FF5252",
        info: "#2196F3",
        success: "#4CAF50",
        warning: "#fb8c00",
      },
    },
  },
})
