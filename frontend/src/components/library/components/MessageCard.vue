<template>
  <div
    class="card bg-base-100 shadow-md hover:shadow-lg transition-all duration-200 border border-base-300"
    :class="{
      'ring-2 ring-primary border-primary': isSelected,
      'cursor-pointer': selectionMode
    }"
    @click="selectionMode && emit('toggle-select', message.id)"
  >
    <div class="card-body p-4">
      <!-- Header: Title + Favorite -->
      <div class="flex items-start justify-between gap-2">
        <!-- Selection checkbox -->
        <input
          v-if="selectionMode"
          type="checkbox"
          class="checkbox checkbox-primary checkbox-sm mt-1"
          :checked="isSelected"
          @click.stop
          @change="emit('toggle-select', message.id)"
        />

        <h3 class="card-title text-base flex-1 line-clamp-2">
          {{ message.display_name }}
        </h3>

        <button
          class="btn btn-ghost btn-sm btn-square"
          :class="{ 'text-warning': message.is_favorite }"
          @click.stop="emit('toggle-favorite', message.id)"
          :title="message.is_favorite ? 'Quitar de favoritos' : 'Agregar a favoritos'"
        >
          <StarIcon
            class="h-5 w-5"
            :class="{ 'fill-current': message.is_favorite }"
          />
        </button>
      </div>

      <!-- Category Badge -->
      <div class="mt-2">
        <CategoryBadge
          :category-id="message.category_id"
          :categories="categories"
          @change="(id) => emit('update-category', message.id, id)"
        />
      </div>

      <!-- Content Preview -->
      <p class="text-sm text-base-content/70 line-clamp-2 mt-2">
        {{ truncate(message.original_text, 100) }}
      </p>

      <!-- Audio Player Row -->
      <div class="flex items-center gap-3 mt-3 pt-3 border-t border-base-300">
        <button
          class="btn btn-circle btn-sm btn-primary"
          @click.stop="emit('play', message)"
          :title="isPlaying ? 'Pausar' : 'Reproducir'"
        >
          <PauseIcon v-if="isPlaying" class="h-4 w-4" />
          <PlayIcon v-else class="h-4 w-4" />
        </button>

        <div class="flex-1 text-sm text-base-content/60">
          {{ formatDuration(message.duration) }}
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-1">
          <button
            class="btn btn-ghost btn-xs btn-square"
            @click.stop="emit('action', 'schedule', message)"
            title="Programar"
          >
            <CalendarIcon class="h-4 w-4" />
          </button>

          <button
            class="btn btn-ghost btn-xs btn-square"
            @click.stop="emit('action', 'send-to-radio', message)"
            title="Enviar a radio"
          >
            <SignalIcon class="h-4 w-4" />
          </button>

          <button
            class="btn btn-ghost btn-xs btn-square"
            @click.stop="emit('action', 'edit-in-dashboard', message)"
            title="Editar copia en Dashboard"
          >
            <PencilSquareIcon class="h-4 w-4" />
          </button>

          <button
            class="btn btn-ghost btn-xs btn-square text-error"
            @click.stop="emit('action', 'delete', message)"
            title="Eliminar"
          >
            <TrashIcon class="h-4 w-4" />
          </button>
        </div>
      </div>

      <!-- Meta Info -->
      <div class="flex items-center justify-between text-xs text-base-content/50 mt-2">
        <span>{{ formatDate(message.created_at) }}</span>
        <span v-if="message.has_jingle" class="badge badge-xs">Con Jingle</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
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
import { formatDuration, formatDate, truncate } from '../utils/formatters'

defineProps<{
  message: AudioMessage
  categories: Category[]
  selectionMode: boolean
  isSelected: boolean
  isPlaying: boolean
}>()

const emit = defineEmits<{
  'play': [message: AudioMessage]
  'toggle-favorite': [id: number]
  'toggle-select': [id: number]
  'update-category': [id: number, categoryId: string | null]
  'action': [action: MessageAction, message: AudioMessage]
}>()
</script>
