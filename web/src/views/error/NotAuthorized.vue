<template>
  <div>
    <h1>Hey, you shouldn't be here.</h1>
    <h3>You are not authorized to do whatever it was you were trying to do.</h3>
    <p>
      If you think this is an error, please
      <a href="https://github.com/mdryden/110yards/issues" target="_blank">contact the admin</a>, and let him know what
      happened.
    </p>
    <v-alert type="error">If this was not an error, stop doing that, ok?</v-alert>
  </div>
</template>

<script>
//todo: log the access failure somehow.
export default {}
</script>
