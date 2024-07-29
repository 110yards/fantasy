<template>
  <v-card>
    <v-card-title>Transactions</v-card-title>
    <v-card-text>
      <v-simple-table>
        <template>
          <thead>
            <tr>
              <th class="text-left">Timestamp</th>
              <th class="text-left">Type</th>
              <th class="text-left">Message</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="transaction in transactions" :key="transaction.id">
              <td>{{ formatDate(transaction.timestamp.toDate()) }}</td>
              <td>{{ transaction.transaction_type }}</td>
              <td>{{ transaction.message }}</td>
            </tr>
          </tbody>
        </template>
      </v-simple-table>
    </v-card-text>
  </v-card>
</template>

<script>
import { firestore } from "../../modules/firebase/index.js"
import { longDate, shortTime } from "../../modules/formatter/index.js"
export default {
  name: "Transactions",
  data() {
    return {
      transactions: null,
    }
  },
  methods: {
    formatDate(date) {
      return `${longDate(date)} - ${shortTime(date)}`
    },
  },
  mounted() {
    let path = "system_transactions"
    let ref = firestore.collection(path).orderBy("timestamp", "desc").limit(50)
    this.$bind("transactions", ref)
  },
}
</script>
