<template>
  <div>
    <p><AppDefaultButton @click="ownershipReport">Ownership report</AppDefaultButton></p>

    <div v-if="reportReady">
      <h2>
        {{ title }} <v-btn icon @click="copyData"><v-icon>mdi-content-copy</v-icon></v-btn>
      </h2>
      <pre id="reportData">{{ reportData }}</pre>
    </div>
  </div>
</template>

<script>
import AppDefaultButton from "../buttons/AppPrimaryButton.vue"
import { ownershipReport } from "../../api/110yards/admin"

export default {
  name: "Reports",
  components: { AppDefaultButton },
  data() {
    return {
      title: null,
      reportData: null,
    }
  },

  computed: {
    reportReady() {
      return this.reportData !== null
    },
  },

  methods: {
    async ownershipReport() {
      this.reportData = await ownershipReport()
      this.title = "Ownership Report"
    },

    async copyData() {
      let range = document.createRange()
      range.selectNode(document.getElementById("reportData"))
      window.getSelection().removeAllRanges()
      window.getSelection().addRange(range)
      document.execCommand("copy")
      window.getSelection().removeAllRanges()
    },
  },
}
</script>
