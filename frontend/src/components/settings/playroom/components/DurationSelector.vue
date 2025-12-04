<template>
  <div class="form-control">
    <label class="label">
      <span class="label-text font-medium">Duración Objetivo</span>
    </label>
    <div class="flex flex-wrap gap-2">
      <button
        v-for="duration in durations"
        :key="duration"
        @click="$emit('update:target-duration', duration)"
        class="btn btn-sm"
        :class="{
          'btn-primary': targetDuration === duration,
          'btn-outline': targetDuration !== duration
        }"
      >
        {{ duration }}s
      </button>
    </div>
    <label class="label">
      <span class="label-text-alt text-base-content/50">
        {{ wordLimits.min }}-{{ wordLimits.max }} palabras recomendadas
      </span>
    </label>
  </div>
</template>

<script setup lang="ts">
const durations = [5, 10, 15, 20, 25]

defineProps<{
  targetDuration: number
  wordLimits: { min: number; max: number }
}>()

defineEmits<{
  (e: 'update:target-duration', value: number): void
}>()
</script>
