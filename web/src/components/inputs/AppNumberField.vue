<template>
  <v-text-field
    v-model.number="model"
    type="number"
    outlined
    filled
    dense
    :label="calculatedLabel"
    :rules="rules"
    :readonly="readonly"
    :disabled="disabled"
    :required="required"
    :max="max"
    :min="min"
    :prepend-icon="prependIcon"
    :prepend-inner-icon="prependInnerIcon"
  />
</template>

<script>
export default {
  props: {
    value: {
      type: Number,
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
    max: {
      type: String,
      required: false,
    },
    min: {
      type: String,
      required: false,
      default: "0",
    },
    prependIcon: {
      type: String,
      required: false,
    },
    prependInnerIcon: {
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
