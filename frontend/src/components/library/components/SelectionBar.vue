<template>
  <div class="flex items-center justify-between p-3 bg-primary/10 rounded-lg border border-primary/30">
    <div class="flex items-center gap-3">
      <span class="font-medium text-primary">
        {{ selectedCount }} seleccionado{{ selectedCount > 1 ? 's' : '' }}
      </span>
    </div>

    <div class="flex items-center gap-2">
      <!-- Batch categorize -->
      <div class="dropdown dropdown-end">
        <label tabindex="0" class="btn btn-sm btn-ghost">
          <FolderIcon class="h-4 w-4" />
          Categorizar
        </label>
        <ul tabindex="0" class="dropdown-content z-50 menu p-2 shadow-lg bg-base-100 rounded-box w-52">
          <li v-for="cat in categories" :key="cat.id">
            <a @click="emit('categorize', cat.id)">
              <span :style="{ color: cat.color }">{{ cat.icon }}</span>
              {{ cat.name }}
            </a>
          </li>
          <li class="menu-title">
            <span>Sin categoria</span>
          </li>
          <li>
            <a @click="emit('categorize', null)">
              📁 Quitar categoria
            </a>
          </li>
        </ul>
      </div>

      <!-- Delete -->
      <button
        class="btn btn-sm btn-error btn-outline"
        @click="emit('delete')"
      >
        <TrashIcon class="h-4 w-4" />
        Eliminar
      </button>

      <!-- Cancel -->
      <button
        class="btn btn-sm btn-ghost"
        @click="emit('cancel')"
      >
        Cancelar
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FolderIcon, TrashIcon } from '@heroicons/vue/24/outline'
import type { Category } from '@/types/audio'

defineProps<{
  selectedCount: number
  categories: Category[]
}>()

const emit = defineEmits<{
  'delete': []
  'categorize': [categoryId: string | null]
  'cancel': []
}>()
</script>
