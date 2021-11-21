<template>
  <v-text-field
    v-model="model"
    outlined
    filled
    dense
    :label="calculatedLabel"
    :rules="rules"
    :readonly="readonly"
    :disabled="disabled"
    :required="required"
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
      default: "",
    },
    rules: {
      type: Array,
      required: false,
    },
    disabled: {
      type: Boolean,
      required: false,
      default: false,
    },
    readonly: {
      type: Boolean,
      required: false,
      default: false,
    },
    required: {
      type: Boolean,
      required: false,
      default: false,
    },
    hint: {
      type: String,
      required: false,
    },
  },
  computed: {
    calculatedLabel() {
      return this.required ? `${this.label} *` : this.label
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
