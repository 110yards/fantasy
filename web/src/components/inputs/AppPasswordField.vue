<template>
  <v-text-field
    v-model="model"
    :append-icon="clearText ? 'mdi-eye' : 'mdi-eye-off'"
    :type="clearText ? 'text' : 'password'"
    @click:append="clearText = !clearText"
    outlined
    filled
    dense
    :label="calculatedLabel"
    :rules="rules"
    validate-on-blur
    hint="Must be at least 6 characters"
    required
  />
</template>

<script>
export default {
  props: {
    value: {
      type: String,
    },
    label: {
      type: String,
      required: false,
      default: "Password",
    },
  },
  data() {
    return {
      clearText: false,
      rules: [
        v => !!v || "Password is required",
        v => (!!v && v.length >= 6) || "Password must be at least 6 characters",
      ],
    }
  },
  computed: {
    calculatedLabel() {
      return `${this.label} *`
    },
    model: {
      get() {
        return this.value
      },
      set(value) {
        return this.$emit("input", value)
      },
    },
  },
}
</script>
