<template>
  <div class="flex flex-wrap items-center gap-3 p-4 bg-base-200 rounded-lg">
    <!-- Mobile: Filter Button -->
    <button
      class="md:hidden btn btn-sm btn-ghost"
      :class="{ 'btn-active': filters.category_id }"
      @click="showFilterModal = true"
    >
      <FunnelIcon class="h-4 w-4" />
      <span v-if="filters.category_id" class="badge badge-primary badge-xs">1</span>
    </button>

    <!-- Mobile: Favorites (keep visible) -->
    <button
      class="md:hidden btn btn-sm"
      :class="{
        'btn-warning': filters.is_favorite,
        'btn-ghost': !filters.is_favorite
      }"
      @click="toggleFavorites"
    >
      <StarIcon class="h-4 w-4" :class="{ 'fill-current': filters.is_favorite }" />
    </button>

    <!-- Desktop: Search -->
    <div class="hidden md:block form-control flex-1 min-w-[200px]">
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

    <!-- Desktop: Category Filter -->
    <select
      class="hidden md:block select select-sm select-bordered min-w-[150px]"
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

    <!-- Desktop: Favorites Filter -->
    <button
      class="hidden md:inline-flex btn btn-sm"
      :class="{
        'btn-warning': filters.is_favorite,
        'btn-ghost': !filters.is_favorite
      }"
      @click="toggleFavorites"
    >
      <StarIcon class="h-4 w-4" :class="{ 'fill-current': filters.is_favorite }" />
      Favoritos
    </button>

    <!-- Desktop: Sort -->
    <select
      class="hidden md:block select select-sm select-bordered"
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

    <!-- Desktop: Clear Filters -->
    <button
      v-if="hasActiveFilters"
      class="hidden md:inline-flex btn btn-sm btn-ghost text-error"
      @click="emit('reset')"
    >
      <XMarkIcon class="h-4 w-4" />
      Limpiar
    </button>
  </div>

  <!-- Mobile Filter Modal -->
  <dialog ref="filterModalRef" class="modal modal-bottom">
    <div class="modal-box rounded-t-3xl p-0">
      <!-- Header -->
      <div class="p-4 border-b border-base-300">
        <h3 class="font-bold text-lg text-center">Categorías</h3>
      </div>

      <!-- Categories List -->
      <ul class="menu p-2">
        <li>
          <button
            class="flex justify-between"
            :class="{ 'active': !filters.category_id }"
            @click="emit('update:filters', { category_id: null }); showFilterModal = false"
          >
            <span>Todas las categorías</span>
            <span v-if="!filters.category_id" class="text-primary">✓</span>
          </button>
        </li>
        <li v-for="cat in categories" :key="cat.id">
          <button
            class="flex justify-between"
            :class="{ 'active': filters.category_id === cat.id }"
            @click="emit('update:filters', { category_id: cat.id }); showFilterModal = false"
          >
            <span>{{ cat.name }}</span>
            <span v-if="filters.category_id === cat.id" class="text-primary">✓</span>
          </button>
        </li>
      </ul>

      <!-- Clear filters -->
      <div v-if="filters.category_id || filters.is_favorite" class="p-4 border-t border-base-300">
        <button
          class="btn btn-ghost text-error w-full"
          @click="emit('reset'); showFilterModal = false"
        >
          Limpiar filtros
        </button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop">
      <button @click="showFilterModal = false">close</button>
    </form>
  </dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { MagnifyingGlassIcon, XMarkIcon, StarIcon, FunnelIcon } from '@heroicons/vue/24/outline'
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

// Modal state
const showFilterModal = ref(false)
const filterModalRef = ref<HTMLDialogElement | null>(null)

// Watch modal state to open/close dialog
watch(showFilterModal, (show) => {
  if (show) {
    filterModalRef.value?.showModal()
  } else {
    filterModalRef.value?.close()
  }
})

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
