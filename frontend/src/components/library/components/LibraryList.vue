<template>
  <div class="overflow-x-auto">
    <table class="table table-zebra w-full">
      <thead>
        <tr>
          <th v-if="selectionMode" class="w-10">
            <input
              type="checkbox"
              class="checkbox checkbox-sm"
              :checked="allSelected"
              :indeterminate="someSelected && !allSelected"
              @change="toggleSelectAll"
            />
          </th>
          <th class="w-10"></th>
          <th>Nombre</th>
          <th class="w-40">Categoria</th>
          <th class="w-20 text-center">Duracion</th>
          <th class="w-32">Fecha</th>
          <th class="w-28 text-center">Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="message in messages"
          :key="message.id"
          class="hover"
          :class="{ 'bg-primary/10': isSelected(message.id) }"
        >
          <!-- Checkbox -->
          <td v-if="selectionMode">
            <input
              type="checkbox"
              class="checkbox checkbox-sm checkbox-primary"
              :checked="isSelected(message.id)"
              @change="emit('toggle-select', message.id)"
            />
          </td>

          <!-- Favorite -->
          <td>
            <button
              class="btn btn-ghost btn-xs btn-square"
              :class="{ 'text-warning': message.is_favorite }"
              @click="emit('toggle-favorite', message.id)"
            >
              <StarIcon
                class="h-4 w-4"
                :class="{ 'fill-current': message.is_favorite }"
              />
            </button>
          </td>

          <!-- Name -->
          <td>
            <div class="flex items-center gap-2">
              <button
                class="btn btn-circle btn-xs btn-primary"
                @click="emit('play', message)"
              >
                <PauseIcon v-if="isMessagePlaying(message.id)" class="h-3 w-3" />
                <PlayIcon v-else class="h-3 w-3" />
              </button>
              <span class="font-medium truncate max-w-xs">{{ message.display_name }}</span>
              <span v-if="message.has_jingle" class="badge badge-xs badge-secondary">Jingle</span>
            </div>
          </td>

          <!-- Category -->
          <td>
            <CategoryBadge
              :category-id="message.category_id"
              :categories="categories"
              @change="(id) => emit('update-category', message.id, id)"
            />
          </td>

          <!-- Duration -->
          <td class="text-center text-sm">
            {{ formatDuration(message.duration) }}
          </td>

          <!-- Date -->
          <td class="text-sm text-base-content/70">
            {{ formatDate(message.created_at) }}
          </td>

          <!-- Actions -->
          <td>
            <div class="flex justify-center gap-1">
              <button
                class="btn btn-ghost btn-xs btn-square"
                @click="emit('action', 'schedule', message)"
                title="Programar"
              >
                <CalendarIcon class="h-4 w-4" />
              </button>
              <button
                class="btn btn-ghost btn-xs btn-square"
                @click="emit('action', 'send-to-radio', message)"
                title="Enviar a radio"
              >
                <SignalIcon class="h-4 w-4" />
              </button>
              <button
                class="btn btn-ghost btn-xs btn-square"
                @click="emit('action', 'edit-in-dashboard', message)"
                title="Editar copia"
              >
                <PencilSquareIcon class="h-4 w-4" />
              </button>
              <button
                class="btn btn-ghost btn-xs btn-square text-error"
                @click="emit('action', 'delete', message)"
                title="Eliminar"
              >
                <TrashIcon class="h-4 w-4" />
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  StarIcon,
  PlayIcon,
  PauseIcon,
  CalendarIcon,
  SignalIcon,
  PencilSquareIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'
import type { AudioMessage, Category } from '@/types/audio'
import type { MessageAction } from '../types/library.types'
import CategoryBadge from './CategoryBadge.vue'
import { formatDuration, formatDate } from '../utils/formatters'

const props = defineProps<{
  messages: AudioMessage[]
  categories: Category[]
  selectionMode: boolean
  selectedIds: Set<number>
  isSelected: (id: number) => boolean
  isMessagePlaying: (id: number) => boolean
}>()

const emit = defineEmits<{
  'play': [message: AudioMessage]
  'toggle-favorite': [id: number]
  'toggle-select': [id: number]
  'select-all': [ids: number[]]
  'clear-selection': []
  'update-category': [id: number, categoryId: string | null]
  'action': [action: MessageAction, message: AudioMessage]
}>()

const allSelected = computed(() =>
  props.messages.length > 0 &&
  props.messages.every(m => props.selectedIds.has(m.id))
)

const someSelected = computed(() =>
  props.messages.some(m => props.selectedIds.has(m.id))
)

function toggleSelectAll() {
  if (allSelected.value) {
    emit('clear-selection')
  } else {
    emit('select-all', props.messages.map(m => m.id))
  }
}
</script>
