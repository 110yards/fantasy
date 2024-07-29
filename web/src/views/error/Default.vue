<template>
  <div>
    <h1>Oh no.</h1>
    <h2>Something went wrong. Sorry about that.</h2>
    <p>
      The error has been logged, but you may also want to
      <a href="https://github.com/mdryden/110yards/issues" target="_blank">contact the admin</a>, and let him know what
      happened.
    </p>
    <v-alert type="error">
      {{ message }}
    </v-alert>
  </div>
</template>

<script>
//todo: log the error somehow.  stack driver? sentry? (either way, needs an abstraction)
export default {
  computed: {
    message() {
      return this.$route.params.message
    },
  },
}
</script>
