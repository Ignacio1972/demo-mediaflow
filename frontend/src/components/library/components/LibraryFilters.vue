<template>
  <div class="flex flex-wrap items-center gap-3 p-4 bg-base-200 rounded-lg">
    <!-- Search -->
    <div class="form-control flex-1 min-w-[200px]">
      <div class="input-group input-group-sm">
        <span class="bg-base-300">
          <MagnifyingGlassIcon class="h-4 w-4" />
        </span>
        <input
          type="text"
          class="input input-sm input-bordered flex-1"
          placeholder="Buscar mensajes..."
          :value="filters.search"
          @input="onSearchInput"
        />
        <button
          v-if="filters.search"
          class="btn btn-sm btn-ghost"
          @click="emit('update:filters', { ...filters, search: '' })"
        >
          <XMarkIcon class="h-4 w-4" />
        </button>
      </div>
    </div>

    <!-- Category Filter -->
    <select
      class="select select-sm select-bordered min-w-[150px]"
      :value="filters.category_id || ''"
      @change="onCategoryChange"
    >
      <option value="">Todas las categorias</option>
      <option
        v-for="cat in categories"
        :key="cat.id"
        :value="cat.id"
      >
        {{ cat.name }}
      </option>
    </select>

    <!-- Favorites Filter -->
    <button
      class="btn btn-sm"
      :class="{
        'btn-warning': filters.is_favorite,
        'btn-ghost': !filters.is_favorite
      }"
      @click="toggleFavorites"
    >
      <StarIcon class="h-4 w-4" :class="{ 'fill-current': filters.is_favorite }" />
      Favoritos
    </button>

    <!-- Sort -->
    <select
      class="select select-sm select-bordered"
      :value="`${filters.sort_by}_${filters.sort_order}`"
      @change="onSortChange"
    >
      <option value="created_at_desc">Mas recientes</option>
      <option value="created_at_asc">Mas antiguos</option>
      <option value="display_name_asc">Nombre A-Z</option>
      <option value="display_name_desc">Nombre Z-A</option>
      <option value="duration_desc">Mayor duracion</option>
      <option value="duration_asc">Menor duracion</option>
    </select>

    <!-- Clear Filters -->
    <button
      v-if="hasActiveFilters"
      class="btn btn-sm btn-ghost text-error"
      @click="emit('reset')"
    >
      <XMarkIcon class="h-4 w-4" />
      Limpiar
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { MagnifyingGlassIcon, XMarkIcon, StarIcon } from '@heroicons/vue/24/outline'
import type { Category } from '@/types/audio'
import type { LibraryFilters } from '../types/library.types'

const props = defineProps<{
  filters: LibraryFilters
  categories: Category[]
}>()

const emit = defineEmits<{
  'update:filters': [filters: Partial<LibraryFilters>]
  'reset': []
}>()

const hasActiveFilters = computed(() =>
  props.filters.search ||
  props.filters.category_id ||
  props.filters.is_favorite
)

let searchTimeout: number | null = null

function onSearchInput(event: Event) {
  const value = (event.target as HTMLInputElement).value

  // Debounce search
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = window.setTimeout(() => {
    emit('update:filters', { search: value })
  }, 300)
}

function onCategoryChange(event: Event) {
  const value = (event.target as HTMLSelectElement).value
  emit('update:filters', { category_id: value || null })
}

function toggleFavorites() {
  emit('update:filters', {
    is_favorite: props.filters.is_favorite ? null : true
  })
}

function onSortChange(event: Event) {
  const value = (event.target as HTMLSelectElement).value
  const [sort_by, sort_order] = value.split('_') as [LibraryFilters['sort_by'], LibraryFilters['sort_order']]
  emit('update:filters', { sort_by, sort_order })
}
</script>
