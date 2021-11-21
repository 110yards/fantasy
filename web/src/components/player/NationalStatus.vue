<template>
  <v-icon v-if="national_status == 'N'" x-small color="red" class="mb-1">mdi-leaf-maple</v-icon>
</template>

<script>
export default {
  name: "NationalStatus",
  props: {
    national_status: {
      type: String,
      required: false,
    },
  },
}
</script>
