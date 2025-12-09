<template>
  <div
    class="card bg-base-100 border-2 cursor-pointer transition-all duration-200 hover:shadow-md"
    :class="{
      'border-primary shadow-lg': isSelected,
      'border-base-300 hover:border-primary/50': !isSelected
    }"
    @click="$emit('select', client)"
  >
    <div class="card-body p-4">
      <div class="flex items-start justify-between gap-2">
        <div class="flex-1 min-w-0">
          <h3 class="font-semibold text-base-content truncate">
            {{ client.name }}
          </h3>
          <p class="text-xs text-base-content/60 mt-1">
            {{ client.category }}
          </p>
        </div>
        <div class="flex flex-col items-end gap-1">
          <span
            v-if="client.is_default"
            class="badge badge-primary badge-sm"
          >
            Activo
          </span>
          <span
            v-if="!client.active"
            class="badge badge-ghost badge-sm"
          >
            Inactivo
          </span>
        </div>
      </div>
      <p class="text-xs text-base-content/50 mt-2 line-clamp-2">
        {{ truncatedContext }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AIClient } from '@/composables/useAIClients'

const props = defineProps<{
  client: AIClient
  isSelected: boolean
}>()

defineEmits<{
  select: [client: AIClient]
}>()

const truncatedContext = computed(() => {
  const ctx = props.client.context
  return ctx.length > 100 ? ctx.substring(0, 100) + '...' : ctx
})
</script>
