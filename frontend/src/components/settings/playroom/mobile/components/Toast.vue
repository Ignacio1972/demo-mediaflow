<template>
  <Teleport to="body">
    <Transition name="toast">
      <div
        v-if="message"
        class="fixed bottom-20 left-4 right-4 z-50 flex justify-center"
      >
        <div class="alert shadow-lg max-w-sm" :class="alertClass">
          <span>{{ message }}</span>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Props
interface Props {
  message: string | null
  type?: 'success' | 'error' | 'info' | 'warning'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'success'
})

const alertClass = computed(() => {
  switch (props.type) {
    case 'success':
      return 'alert-success'
    case 'error':
      return 'alert-error'
    case 'warning':
      return 'alert-warning'
    case 'info':
    default:
      return 'alert-info'
  }
})
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
