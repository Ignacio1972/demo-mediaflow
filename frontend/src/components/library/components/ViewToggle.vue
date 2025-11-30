<template>
  <div class="btn-group">
    <button
      class="btn btn-sm"
      :class="{ 'btn-active': modelValue === 'grid' }"
      @click="emit('update:modelValue', 'grid')"
      title="Vista Grid"
    >
      <Squares2X2Icon class="h-4 w-4" />
    </button>
    <button
      class="btn btn-sm"
      :class="{ 'btn-active': modelValue === 'list' }"
      @click="emit('update:modelValue', 'list')"
      title="Vista Lista"
    >
      <ListBulletIcon class="h-4 w-4" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { Squares2X2Icon, ListBulletIcon } from '@heroicons/vue/24/outline'
import type { ViewMode } from '../types/library.types'

defineProps<{
  modelValue: ViewMode
}>()

const emit = defineEmits<{
  'update:modelValue': [value: ViewMode]
}>()
</script>
