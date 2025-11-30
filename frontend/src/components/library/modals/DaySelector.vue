<template>
  <div>
    <label class="label"><span class="label-text">Dias de la semana:</span></label>
    <div class="flex flex-wrap gap-2">
      <button
        v-for="day in days"
        :key="day.value"
        class="btn btn-sm"
        :class="{
          'btn-primary': modelValue.includes(day.value),
          'btn-outline': !modelValue.includes(day.value)
        }"
        @click="toggleDay(day.value)"
      >
        {{ day.label }}
      </button>
    </div>
    <div class="flex gap-2 mt-2">
      <button class="btn btn-xs btn-ghost" @click="selectWeekdays">
        L-V
      </button>
      <button class="btn btn-xs btn-ghost" @click="selectWeekend">
        S-D
      </button>
      <button class="btn btn-xs btn-ghost" @click="selectAll">
        Todos
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const days = [
  { value: 0, label: 'Dom' },
  { value: 1, label: 'Lun' },
  { value: 2, label: 'Mar' },
  { value: 3, label: 'Mie' },
  { value: 4, label: 'Jue' },
  { value: 5, label: 'Vie' },
  { value: 6, label: 'Sab' }
]

const props = defineProps<{
  modelValue: number[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number[]]
}>()

function toggleDay(day: number) {
  const newValue = props.modelValue.includes(day)
    ? props.modelValue.filter(d => d !== day)
    : [...props.modelValue, day].sort((a, b) => a - b)
  emit('update:modelValue', newValue)
}

function selectWeekdays() {
  emit('update:modelValue', [1, 2, 3, 4, 5])
}

function selectWeekend() {
  emit('update:modelValue', [0, 6])
}

function selectAll() {
  emit('update:modelValue', [0, 1, 2, 3, 4, 5, 6])
}
</script>
