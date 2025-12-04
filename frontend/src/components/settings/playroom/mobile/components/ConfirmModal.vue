<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="$emit('cancel')"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>

        <!-- Modal Card -->
        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden animate-modal-enter">
          <!-- Header -->
          <div class="p-6 text-center">
            <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-base-content mb-2">
              Confirmar Envío
            </h3>
            <p class="text-base-content/70">
              ¿Enviar este mensaje a los parlantes ahora?
            </p>
          </div>

          <!-- Actions -->
          <div class="p-4 pt-0 flex flex-col gap-3">
            <button
              @click="$emit('confirm')"
              class="btn btn-primary btn-lg w-full gap-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              Sí, Enviar
            </button>
            <button
              @click="$emit('cancel')"
              class="btn btn-ghost w-full"
            >
              Cancelar
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
// Props
interface Props {
  show: boolean
}

defineProps<Props>()

// Emits
defineEmits<{
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()
</script>

<style scoped>
/* Modal transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .animate-modal-enter,
.modal-leave-active .animate-modal-enter {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.modal-enter-from .animate-modal-enter {
  transform: scale(0.95);
  opacity: 0;
}

.modal-leave-to .animate-modal-enter {
  transform: scale(0.95);
  opacity: 0;
}

@keyframes modal-enter {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.animate-modal-enter {
  animation: modal-enter 0.2s ease forwards;
}
</style>
