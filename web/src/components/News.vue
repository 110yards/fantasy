<template>
  <div v-if="!error">
    <v-card>
      <v-card-text>
        <div class="news-item" v-for="item in news" :key="item.guid">
          <h4>
            <a :href="item.link" target="_blank">{{ item.title }}</a>
          </h4>
          <p class="text-body-2">{{ item.description }}</p>
        </div>
      </v-card-text>
    </v-card>

    <!-- <v-list>
      <v-list-item v-for="item in news" :key="item.id">
        <v-list-item-content>
          <v-list-item-title
            ><a :href="item.link">{{ item.title }}</a></v-list-item-title
          >
          <v-list-item-subtitle>{{ item.description }}</v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </v-list> -->

    <h5 class="ma-2">News powered by <a href="https://cflnewshub.com" target="_blank">CFL News Hub</a></h5>
  </div>
  <div v-else>Failed to retrieve news</div>
</template>

<script>
import { getNews } from "../api/110yards/news"

export default {
  name: "News",

  data() {
    return {
      news: [],
      error: false,
    }
  },

  methods: {
    async loadNews() {
      try {
        this.news = await getNews()
        this.error = false
      } catch (error) {
        this.error = true
      }
    },
  },

  mounted() {
    this.loadNews()
  },
}
</script>
