<template>
  <div>
    <ReviewPassing :season="season" :players="players" />
    <ReviewRushing class="mt-6" :season="season" :players="players" />
    <ReviewReceiving class="mt-6" :season="season" :players="players" />
    <ReviewDefense class="mt-6" :season="season" :players="players" />
    <ReviewKicking class="mt-6" :season="season" :players="players" />
    <ReviewPunting class="mt-6" :season="season" :players="players" />
  </div>
</template>

<script>
import ReviewPassing from "./ReviewPassing.vue"
import ReviewRushing from "./ReviewRushing.vue"
import ReviewReceiving from "./ReviewReceiving.vue"
import ReviewDefense from "./ReviewDefense.vue"
import ReviewKicking from "./ReviewKicking.vue"
import ReviewPunting from "./ReviewPunting.vue"

export default {
  name: "ReviewTeam",
  components: {
    ReviewPassing,
    ReviewRushing,
    ReviewReceiving,
    ReviewDefense,
    ReviewKicking,
    ReviewPunting,
  },
  props: {
    season: {
      type: Number,
      required: true,
    },
    players: {
      type: Array,
      required: true,
    },
  },
  computed: {},
}
</script>
