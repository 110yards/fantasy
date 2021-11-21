<template>
  <section id="transactions">
    <v-card>
      <v-card-title class="subtitle-1">
        <span v-if="!showAll">Last 10 league transactions</span>
        <h5 v-else>All league transactions</h5>
      </v-card-title>

      <v-card-text>
        <v-row>
          <v-col cols="12">
            <p v-for="transaction in transactions" :key="transaction.id" class="transaction caption">
              {{ formatTimestamp(transaction.timestamp) }} -
              <span :class="getMessageClass(transaction)">{{ transaction.message }}</span>
            </p>
          </v-col>

          <v-btn v-if="!showAll" link @click="showAll = true"> Show all</v-btn>
        </v-row>
      </v-card-text>
    </v-card>
  </section>
</template>

<style scoped>
#transactions {
  color: var(--text-color);
}
</style>

<script>
import { transactionType } from "../../api/110yards/constants"
import { firestore } from "../../modules/firebase"
import { relativeDateTime } from "../../modules/formatter"
export default {
  name: "Transactions",

  props: {
    leagueId: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      transactions: [],
      showAll: false,
    }
  },

  methods: {
    configureBindings() {
      let transactionsRef = firestore.collection(`league/${this.leagueId}/transaction`).orderBy("timestamp", "desc")

      if (!this.showAll) {
        transactionsRef = transactionsRef.limit(10)
      }

      this.$bind("transactions", transactionsRef)
    },

    formatTimestamp(timestamp) {
      let ts = timestamp.toDate()
      let formatted = relativeDateTime(ts)
      return formatted[0].toUpperCase() + formatted.slice(1)
    },

    getMessageClass(transaction) {
      return transactionType.isCommissionerChange(transaction.type) ? "red--text" : null
    },
  },

  watch: {
    leagueId: {
      immediate: true,
      handler(leagueId) {
        if (leagueId) {
          this.configureBindings()
        }
      },
    },

    showAll: {
      handler(showAll) {
        if (showAll) {
          this.configureBindings()
        }
      },
    },
  },
}
</script>
