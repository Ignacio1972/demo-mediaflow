<script setup lang="ts">
import { useRouter } from 'vue-router'
import { BoltIcon } from '@heroicons/vue/24/outline'
import OperationCard, { type Operation } from './components/OperationCard.vue'

const router = useRouter()

// Available operations
const operations: Operation[] = [
  {
    id: 'vehicles',
    name: 'Vehículos Mal Estacionados',
    description: 'Anuncios con pronunciación correcta de patentes',
    icon: 'Truck',
    path: '/operations/vehicles',
    available: true,
  },
  {
    id: 'schedules',
    name: 'Horarios',
    description: 'Anuncios de apertura y cierre del local',
    icon: 'Clock',
    path: '/operations/schedules',
    available: true,
  },
  {
    id: 'employee-call',
    name: 'Llamado a\nEmpleado o Cliente',
    description: 'Solicitar presencia de un trabajador o cliente',
    icon: 'Phone',
    path: '/operations/employee-call',
    available: true,
  },
]

function handleOperationClick(operation: Operation) {
  router.push(operation.path)
}
</script>

<template>
  <div class="min-h-screen bg-base-100">
    <div class="container mx-auto px-6 py-8 max-w-5xl">
      <!-- Header Section -->
      <div class="mb-10">
        <div class="flex items-center gap-3 mb-2">
          <div class="flex items-center justify-center w-10 h-10 bg-primary/10 rounded-xl">
            <BoltIcon class="w-5 h-5 text-primary" />
          </div>
          <h1 class="text-3xl font-bold tracking-tight">Operaciones</h1>
        </div>
        <p class="text-base-content/50 ml-13">
          Anuncios rápidos para situaciones del día a día
        </p>
      </div>

      <!-- Operations Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <OperationCard
          v-for="(operation, index) in operations"
          :key="operation.id"
          :operation="operation"
          :style="{ animationDelay: `${index * 80}ms` }"
          class="operation-card-enter"
          @click="handleOperationClick"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.ml-13 {
  margin-left: 3.25rem;
}

/* Staggered entrance animation */
.operation-card-enter {
  animation: cardEnter 0.4s ease-out backwards;
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>
