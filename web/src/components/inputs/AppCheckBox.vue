<template>
  <v-checkbox
    v-model="model"
    solo-inverted
    dense
    :label="label"
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
  },
  computed: {
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
