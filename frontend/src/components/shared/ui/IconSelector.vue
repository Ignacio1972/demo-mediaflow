<script setup lang="ts">
import { ref, computed } from 'vue'
import DynamicIcon from './DynamicIcon.vue'
import { iconCategories } from './icons'
import { MagnifyingGlassIcon } from '@heroicons/vue/24/outline'

interface Props {
  modelValue: string | null | undefined
  showSearch?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showSearch: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const searchQuery = ref('')

// Filter icons based on search
const filteredCategories = computed(() => {
  if (!searchQuery.value.trim()) {
    return iconCategories
  }

  const query = searchQuery.value.toLowerCase()
  const result: Record<string, string[]> = {}

  for (const [category, icons] of Object.entries(iconCategories)) {
    const filtered = icons.filter(icon =>
      icon.toLowerCase().includes(query) ||
      category.toLowerCase().includes(query)
    )
    if (filtered.length > 0) {
      result[category] = filtered
    }
  }

  return result
})

// Check if an icon is selected
function isSelected(iconName: string): boolean {
  return props.modelValue === iconName
}

// Select an icon
function selectIcon(iconName: string) {
  // Toggle if clicking same icon
  if (props.modelValue === iconName) {
    emit('update:modelValue', '')
  } else {
    emit('update:modelValue', iconName)
  }
}
</script>

<template>
  <div class="icon-selector">
    <!-- Search (optional) -->
    <div v-if="showSearch" class="mb-3">
      <div class="relative">
        <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-base-content/40" />
        <input
          v-model="searchQuery"
          type="text"
          class="input input-bordered input-sm w-full pl-9"
          placeholder="Buscar icono..."
        />
      </div>
    </div>

    <!-- Icon Categories -->
    <div class="space-y-3">
      <template v-for="(icons, category) in filteredCategories" :key="category">
        <div>
          <p class="text-xs font-medium text-base-content/50 mb-1.5">{{ category }}</p>
          <div class="flex flex-wrap gap-1">
            <button
              v-for="iconName in icons"
              :key="iconName"
              type="button"
              class="btn btn-square btn-sm transition-all"
              :class="[
                isSelected(iconName)
                  ? 'btn-primary'
                  : 'btn-ghost hover:btn-outline'
              ]"
              :title="iconName"
              @click="selectIcon(iconName)"
            >
              <DynamicIcon :name="iconName" class="w-5 h-5" />
            </button>
          </div>
        </div>
      </template>
    </div>

    <!-- Empty state -->
    <div
      v-if="Object.keys(filteredCategories).length === 0"
      class="text-center py-4 text-base-content/50 text-sm"
    >
      No se encontraron iconos
    </div>
  </div>
</template>

<style scoped>
.icon-selector {
  max-height: 280px;
  overflow-y: auto;
}
</style>
