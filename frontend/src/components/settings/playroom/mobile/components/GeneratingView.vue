<template>
  <div class="generating-view h-full flex flex-col items-center justify-center p-6 bg-base-100">
    <!-- Magic wand animation container -->
    <div class="magic-container mb-8">
      <div class="magic-circle w-32 h-32 rounded-full bg-primary/10 flex items-center justify-center">
        <span class="loading loading-spinner loading-lg text-primary"></span>
      </div>

      <!-- Sparkles around the circle -->
      <div class="sparkle sparkle-1"></div>
      <div class="sparkle sparkle-2"></div>
      <div class="sparkle sparkle-3"></div>
      <div class="sparkle sparkle-4"></div>
    </div>

    <!-- Message -->
    <div class="text-center">
      <h2 class="text-2xl font-bold text-base-content mb-2">
        Haciendo la magia...
      </h2>
      <p class="text-base-content/60">
        {{ currentStep }}
      </p>
    </div>

    <!-- Progress dots -->
    <div class="flex items-center gap-2 mt-8">
      <div
        v-for="i in 3"
        :key="i"
        class="w-3 h-3 rounded-full transition-colors duration-300"
        :class="i <= step ? 'bg-primary' : 'bg-base-300'"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

// Steps for the generation process
const steps = [
  'Mejorando tu texto con IA...',
  'Generando la voz...',
  'Preparando el audio...',
]

const step = ref(1)
const currentStep = ref(steps[0])

let stepInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  // Cycle through steps for visual feedback
  stepInterval = setInterval(() => {
    step.value = (step.value % 3) + 1
    currentStep.value = steps[step.value - 1]
  }, 2000)
})

onUnmounted(() => {
  if (stepInterval) {
    clearInterval(stepInterval)
  }
})
</script>

<style scoped>
.generating-view {
  background: radial-gradient(circle at center, oklch(var(--p) / 0.05) 0%, transparent 70%);
}

.magic-container {
  position: relative;
}

.magic-circle {
  animation: float 2s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

/* Sparkle animations */
.sparkle {
  position: absolute;
  width: 8px;
  height: 8px;
  background: oklch(var(--p));
  border-radius: 50%;
  animation: sparkle 1.5s ease-in-out infinite;
}

.sparkle-1 {
  top: 0;
  left: 50%;
  animation-delay: 0s;
}

.sparkle-2 {
  top: 50%;
  right: 0;
  animation-delay: 0.3s;
}

.sparkle-3 {
  bottom: 0;
  left: 50%;
  animation-delay: 0.6s;
}

.sparkle-4 {
  top: 50%;
  left: 0;
  animation-delay: 0.9s;
}

@keyframes sparkle {
  0%, 100% {
    opacity: 0;
    transform: scale(0);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
