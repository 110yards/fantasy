<template>
  <v-icon v-if="isCanadian" x-small color="red" class="mb-1">mdi-leaf-maple</v-icon>
</template>

<script>
export default {
  name: "CanadianStatus",
  props: {
    isCanadian: {
      type: Boolean,
      required: false,
    },
  },
}
</script>
