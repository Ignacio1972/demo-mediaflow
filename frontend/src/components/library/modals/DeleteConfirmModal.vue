<template>
  <dialog class="modal" :class="{ 'modal-open': open }">
    <div class="modal-box max-w-sm">
      <h3 class="font-bold text-lg flex items-center gap-2 text-error">
        <ExclamationTriangleIcon class="h-6 w-6" />
        Confirmar eliminacion
      </h3>

      <p class="py-4">
        {{ message }}
      </p>

      <div class="modal-action">
        <button class="btn btn-ghost" @click="emit('update:open', false)">
          Cancelar
        </button>
        <button class="btn btn-error" @click="confirm">
          Eliminar
        </button>
      </div>
    </div>

    <form method="dialog" class="modal-backdrop">
      <button @click="emit('update:open', false)">close</button>
    </form>
  </dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

const props = defineProps<{
  open: boolean
  count: number
  itemName?: string
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'confirm': []
}>()

const message = computed(() => {
  if (props.itemName) {
    return `¿Seguro que deseas eliminar "${props.itemName}"? Esta accion no se puede deshacer.`
  }
  if (props.count === 1) {
    return '¿Seguro que deseas eliminar este mensaje? Esta accion no se puede deshacer.'
  }
  return `¿Seguro que deseas eliminar ${props.count} mensajes? Esta accion no se puede deshacer.`
})

function confirm() {
  emit('confirm')
  emit('update:open', false)
}
</script>
