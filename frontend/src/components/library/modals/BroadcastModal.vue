<template>
  <dialog class="modal" :class="{ 'modal-open': open }">
    <div class="modal-box max-w-md">
      <!-- Header -->
      <div class="flex items-center gap-3 mb-6">
        <div class="p-2 bg-primary/10 rounded-lg">
          <SignalIcon class="h-6 w-6 text-primary" />
        </div>
        <h2 class="text-2xl font-bold">Enviar a los parlantes</h2>
      </div>

      <!-- Divider -->
      <div class="divider text-sm text-base-content/50 mt-0">Selecciona destino</div>

      <!-- Branch Selection -->
      <div class="space-y-3">
        <!-- Select All -->
        <label class="flex items-center gap-3 cursor-pointer p-3 rounded-lg bg-primary/5 hover:bg-primary/10 transition-colors border border-primary/20">
          <input
            type="checkbox"
            class="checkbox checkbox-primary"
            :checked="allSelected"
            @change="toggleAll"
          />
          <span class="font-medium">Enviar a todas las sucursales</span>
        </label>

        <!-- Individual Branches -->
        <div class="grid grid-cols-2 gap-2">
          <label
            v-for="branch in branches"
            :key="branch.id"
            class="flex items-center gap-2 cursor-pointer p-2 rounded-lg hover:bg-base-200 transition-colors"
          >
            <input
              type="checkbox"
              class="checkbox checkbox-sm"
              :checked="selectedBranches.includes(branch.id)"
              @change="toggleBranch(branch.id)"
            />
            <span class="text-sm">{{ branch.name }}</span>
          </label>
        </div>
      </div>

      <!-- Actions -->
      <div class="modal-action">
        <button class="btn btn-ghost" @click="close">
          Cancelar
        </button>
        <button
          class="btn btn-primary"
          :disabled="selectedBranches.length === 0 || isSending"
          @click="send"
        >
          <span v-if="isSending" class="loading loading-spinner loading-sm"></span>
          <template v-else>
            <SignalIcon class="h-4 w-4" />
            Enviar
            <span v-if="selectedBranches.length > 0" class="badge badge-sm">
              {{ selectedBranches.length }}
            </span>
          </template>
        </button>
      </div>
    </div>

    <form method="dialog" class="modal-backdrop">
      <button @click="close">close</button>
    </form>
  </dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { SignalIcon } from '@heroicons/vue/24/solid'
import type { AudioMessage } from '@/types/audio'

defineProps<{
  open: boolean
  message: AudioMessage | null
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'sent': [branchCount: number]
}>()

// Placeholder branches
const branches = [
  { id: 'A', name: 'Sucursal A' },
  { id: 'B', name: 'Sucursal B' },
  { id: 'C', name: 'Sucursal C' },
  { id: 'D', name: 'Sucursal D' },
  { id: 'E', name: 'Sucursal E' },
  { id: 'F', name: 'Sucursal F' }
]

const selectedBranches = ref<string[]>([])
const isSending = ref(false)

const allSelected = computed(() =>
  selectedBranches.value.length === branches.length
)

function toggleAll() {
  if (allSelected.value) {
    selectedBranches.value = []
  } else {
    selectedBranches.value = branches.map(b => b.id)
  }
}

function toggleBranch(id: string) {
  const index = selectedBranches.value.indexOf(id)
  if (index === -1) {
    selectedBranches.value.push(id)
  } else {
    selectedBranches.value.splice(index, 1)
  }
}

async function send() {
  if (selectedBranches.value.length === 0) return

  isSending.value = true

  try {
    // Simulate sending (placeholder)
    await new Promise(resolve => setTimeout(resolve, 1000))

    const count = selectedBranches.value.length
    emit('sent', count)
    close()
  } finally {
    isSending.value = false
  }
}

function close() {
  selectedBranches.value = []
  emit('update:open', false)
}
</script>
