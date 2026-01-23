<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title text-lg mb-4">
        <BoltIcon class="w-5 h-5" />
        Shortcuts
        <span class="badge badge-ghost">{{ shortcuts.length }}</span>
      </h2>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex justify-center py-8">
        <span class="loading loading-spinner loading-lg text-primary"></span>
      </div>

      <!-- Empty State -->
      <div v-else-if="shortcuts.length === 0" class="text-center py-8">
        <div class="text-4xl mb-2">⚡</div>
        <p class="text-base-content/50">No hay shortcuts configurados</p>
        <p class="text-sm text-base-content/40 mt-1">
          Crea uno para empezar
        </p>
      </div>

      <!-- Shortcut List -->
      <div v-else class="space-y-2 max-h-96 overflow-y-auto">
        <ShortcutCard
          v-for="shortcut in shortcuts"
          :key="shortcut.id"
          :shortcut="shortcut"
          :is-selected="selectedShortcut?.id === shortcut.id"
          @click="$emit('select', shortcut)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { BoltIcon } from '@heroicons/vue/24/outline'
import ShortcutCard from './ShortcutCard.vue'
import type { Shortcut } from '@/types/shortcut'

defineProps<{
  shortcuts: Shortcut[]
  selectedShortcut: Shortcut | null
  isLoading: boolean
}>()

defineEmits<{
  select: [shortcut: Shortcut]
}>()
</script>
