<template>
  <v-select
    v-model="model"
    outlined
    filled
    dense
    :label="calculatedLabel"
    :menu-props="{ top: true, offsetY: true }"
    :rules="rules"
    :items="items"
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
      required: true,
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
    items: {
      type: Array,
      required: true,
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
