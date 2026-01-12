<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body p-4">
      <!-- Loading -->
      <div v-if="isLoading" class="flex justify-center py-8">
        <span class="loading loading-spinner loading-lg text-primary"></span>
      </div>

      <!-- Empty State -->
      <div v-else-if="clients.length === 0" class="text-center py-8">
        <div class="text-4xl mb-2">🤖</div>
        <p class="text-base-content/60">No hay clientes configurados</p>
        <p class="text-xs text-base-content/40 mt-1">
          Agrega tu primer cliente IA
        </p>
      </div>

      <!-- Client List -->
      <div v-else class="space-y-2 max-h-[80vh] overflow-y-auto">
        <TransitionGroup name="list">
          <AIClientCard
            v-for="client in sortedClients"
            :key="client.id"
            :client="client"
            :is-selected="selectedClient?.id === client.id"
            @select="$emit('select', client)"
          />
        </TransitionGroup>
      </div>

      <!-- Summary Footer -->
      <div v-if="clients.length > 0" class="mt-4 pt-4 border-t border-base-300">
        <div class="flex justify-between text-xs text-base-content/50">
          <span>{{ activeCount }} activos</span>
          <span v-if="defaultClient">
            Activo: {{ defaultClient.name }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import AIClientCard from './AIClientCard.vue'
import type { AIClient } from '@/composables/useAIClients'

const props = defineProps<{
  clients: AIClient[]
  selectedClient: AIClient | null
  isLoading: boolean
}>()

defineEmits<{
  select: [client: AIClient]
}>()

const sortedClients = computed(() =>
  [...props.clients].sort((a, b) => a.order - b.order)
)

const activeCount = computed(() =>
  props.clients.filter(c => c.active).length
)

const defaultClient = computed(() =>
  props.clients.find(c => c.is_default)
)
</script>

<style scoped>
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
